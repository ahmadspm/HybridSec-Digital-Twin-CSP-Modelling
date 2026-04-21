#!/usr/bin/env python3
"""
Hybrid reasoning engine performance script (analysis, not load/benchmark).
Summarizes latency and scoring characteristics for multiple campaigns and engines.

- Latency metrics sourced from: measurement=cps_pipeline, phase='after_db', field=lat_rules_db_ms
- Scoring metrics sourced from:  measurement=cps_pipeline, phase='score',     field=confidence, tag=conf_band

Outputs (CSV + Markdown) under --out (default: ./out):
  - latency_stats_by_engine.csv
  - confidence_stats_by_engine.csv
  - band_distribution_by_engine.csv
  - per_campaign_engine_summary.csv
  - hybrid_engine_performance_summary.md   (quick narrative summary)

Usage (examples):
  python hybrid_engine_performance.py --host localhost --db k6 --hours 48 --campaigns C0012 --mode 2.0
  python hybrid_engine_performance.py --host localhost --db k6 --hours 72 --campaigns C0012 C0020 C0025 C0028

Environment overrides (optional):
  INFLUX_HOST, INFLUX_PORT, INFLUX_DB, INFLUX_USER, INFLUX_PASSWORD

Requires: influxdb, pandas, numpy
"""
import os
import argparse
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Tuple
from influxdb import InfluxDBClient
import pandas as pd

# -----------------------------
# Helpers
# -----------------------------
def make_where(time_hours: int, campaigns: List[str], mode: str|None) -> str:
    t_clause = f"time > now() - {time_hours}h"
    if campaigns:
        c_list = " OR ".join([f'"campaign"=\'{c}\'' for c in campaigns])
        c_clause = f" AND ({c_list})"
    else:
        c_clause = ""
    m_clause = f" AND \"mode\"='{mode}'" if mode else ""
    return f"{t_clause}{c_clause}{m_clause}"

def to_df(result) -> pd.DataFrame:
    if not result:
        return pd.DataFrame()
    # result is a ResultSet; each (measurement, tags) -> points
    frames = []
    for (ms, tags), points in result.items():
        if not points:
            continue
        df = pd.DataFrame(points)
        if tags:
            for k, v in tags.items():
                df[k] = v
        if ms:
            df["measurement"] = ms
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)

def query(client: InfluxDBClient, q: str):
    return client.query(q)

# -----------------------------
# Metric queries
# -----------------------------
def latency_stats(client: InfluxDBClient, where: str) -> pd.DataFrame:
    q = f'''
    SELECT 
      COUNT("lat_rules_db_ms") AS count,
      MEAN("lat_rules_db_ms")  AS mean_ms,
      PERCENTILE("lat_rules_db_ms", 50) AS p50_ms,
      PERCENTILE("lat_rules_db_ms", 95) AS p95_ms,
      PERCENTILE("lat_rules_db_ms", 99) AS p99_ms
    FROM "cps_pipeline"
    WHERE {where} AND "phase"='after_db'
    GROUP BY "engine"
    '''
    rs = query(client, q)
    df = to_df(rs)
    if df.empty:
        return df
    cols = ["time","count","mean_ms","p50_ms","p95_ms","p99_ms","engine"]
    df = df.reindex(columns=[c for c in cols if c in df.columns])
    # keep only one row per engine (ResultSet produces a single timestamped row)
    df = df.drop(columns=[c for c in ["time"] if c in df.columns], errors="ignore")
    return df

def confidence_stats(client: InfluxDBClient, where: str) -> pd.DataFrame:
    q = f'''
    SELECT 
      COUNT("confidence") AS count,
      MEAN("confidence")  AS mean_conf,
      PERCENTILE("confidence", 50) AS p50_conf,
      PERCENTILE("confidence", 95) AS p95_conf,
      PERCENTILE("confidence", 99) AS p99_conf
    FROM "cps_pipeline"
    WHERE {where} AND "phase"='score'
    GROUP BY "engine"
    '''
    rs = query(client, q)
    df = to_df(rs)
    if df.empty:
        return df
    cols = ["time","count","mean_conf","p50_conf","p95_conf","p99_conf","engine"]
    df = df.reindex(columns=[c for c in cols if c in df.columns])
    df = df.drop(columns=[c for c in ["time"] if c in df.columns], errors="ignore")
    return df

def band_distribution(client: InfluxDBClient, where: str) -> pd.DataFrame:
    q = f'''
    SELECT COUNT("confidence") AS count
    FROM "cps_pipeline"
    WHERE {where} AND "phase"='score'
    GROUP BY "engine", "conf_band"
    '''
    rs = query(client, q)
    df = to_df(rs)
    if df.empty:
        return df
    cols = ["time","count","engine","conf_band"]
    df = df.reindex(columns=[c for c in cols if c in df.columns])
    df = df.drop(columns=[c for c in ["time"] if c in df.columns], errors="ignore")
    # Normalize into percentages per engine
    totals = df.groupby("engine")["count"].sum().rename("total")
    df = df.merge(totals, on="engine", how="left")
    df["pct"] = (df["count"] / df["total"]).round(6)
    return df

def per_campaign_engine_summary(client: InfluxDBClient, campaigns: List[str], mode: str|None, hours: int) -> pd.DataFrame:
    rows = []
    for camp in campaigns:
        where = make_where(hours, [camp], mode)
        lat = latency_stats(client, where)
        conf = confidence_stats(client, where)
        bands = band_distribution(client, where)
        # merge latency + confidence on engine
        merged = None
        if lat is not None and not lat.empty and conf is not None and not conf.empty:
            merged = pd.merge(lat, conf, on="engine", how="outer")
        elif lat is not None and not lat.empty:
            merged = lat
        elif conf is not None and not conf.empty:
            merged = conf
        if merged is None or merged.empty:
            continue
        merged["campaign"] = camp
        # Add high/med/low share columns if bands present
        if bands is not None and not bands.empty:
            piv = bands.pivot_table(index="engine", columns="conf_band", values="pct", aggfunc="sum").reset_index()
            for col in ["high","med","low"]:
                if col not in piv.columns:
                    piv[col] = 0.0
            merged = pd.merge(merged, piv[["engine","low","med","high"]], on="engine", how="left")
        rows.append(merged)
    if not rows:
        return pd.DataFrame()
    out = pd.concat(rows, ignore_index=True).fillna(0)
    # nice ordering
    col_order = [
        "campaign", "engine",
        "count_x","mean_ms","p50_ms","p95_ms","p99_ms",
        "count_y","mean_conf","p50_conf","p95_conf","p99_conf",
        "low","med","high"
    ]
    # rename counts
    out = out.rename(columns={"count_x":"count_latency","count_y":"count_conf"})
    # Only keep present cols
    col_order = [c for c in col_order if c in out.columns]
    return out.reindex(columns=col_order)

# -----------------------------
# Main
# -----------------------------
def main():
    ap = argparse.ArgumentParser(description="Hybrid reasoning engine performance analysis (InfluxDB/InfluxQL)." )
    ap.add_argument("--host", default=os.getenv("INFLUX_HOST", "localhost"))
    ap.add_argument("--port", type=int, default=int(os.getenv("INFLUX_PORT", "8086")))
    ap.add_argument("--db",   default=os.getenv("INFLUX_DB", "k6"))
    ap.add_argument("--user", default=os.getenv("INFLUX_USER", ""))
    ap.add_argument("--password", default=os.getenv("INFLUX_PASSWORD", ""))
    ap.add_argument("--hours", type=int, default=72, help="Lookback window in hours (default: 72h)")
    ap.add_argument("--campaigns", nargs="*", default=["C0012"], help="Campaign(s) to include (default: C0012)")
    ap.add_argument("--mode", default=None, help="Optional mode/version tag filter (e.g., 2.0)")
    ap.add_argument("--out", default="./out", help="Output directory")
    args = ap.parse_args()

    client = InfluxDBClient(host=args.host, port=args.port, database=args.db, username=args.user or None, password=args.password or None)

    os.makedirs(args.out, exist_ok=True)
    where = make_where(args.hours, args.campaigns, args.mode)

    lat = latency_stats(client, where)
    conf = confidence_stats(client, where)
    bands = band_distribution(client, where)
    per_camp = per_campaign_engine_summary(client, args.campaigns, args.mode, args.hours)

    # Write CSVs
    if lat is not None and not lat.empty:
        lat.to_csv(os.path.join(args.out, "latency_stats_by_engine.csv"), index=False)
    if conf is not None and not conf.empty:
        conf.to_csv(os.path.join(args.out, "confidence_stats_by_engine.csv"), index=False)
    if bands is not None and not bands.empty:
        bands.to_csv(os.path.join(args.out, "band_distribution_by_engine.csv"), index=False)
    if per_camp is not None and not per_camp.empty:
        per_camp.to_csv(os.path.join(args.out, "per_campaign_engine_summary.csv"), index=False)

    # Markdown summary (brief)
    lines = []
    lines.append(f"# Hybrid Reasoning Engine Performance Summary")
    lines.append(f"- Time window: last {args.hours}h")
    lines.append(f"- Database: {args.db} @ {args.host}:{args.port}")
    lines.append(f"- Campaigns: {', '.join(args.campaigns)}")
    if args.mode:
        lines.append(f"- Mode: {args.mode}")
    lines.append("")

    def md_table(df: pd.DataFrame, header: str):
        if df is None or df.empty:
            return [f"**{header}:** _no data in window_"]
        # limit floats
        df2 = df.copy()
        for c in df2.columns:
            if df2[c].dtype.kind in "f":
                df2[c] = df2[c].map(lambda x: f"{x:.4f}")
        # render markdown
        md = [f"**{header}:**", "", df2.to_markdown(index=False), ""]
        return md

    lines += md_table(lat, "Latency stats by engine (ms)")
    lines += md_table(conf, "Confidence stats by engine (0..1)")
    lines += md_table(bands, "Band distribution by engine (counts & pct)")
    lines += md_table(per_camp, "Per-campaign per-engine summary")

    with open(os.path.join(args.out, "hybrid_engine_performance_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Written outputs to: {os.path.abspath(args.out)}")

if __name__ == "__main__":
    main()
