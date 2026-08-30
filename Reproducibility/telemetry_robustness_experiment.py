#!/usr/bin/env python3
"""Controlled telemetry-robustness experiment for the HySecTwin smart-lighting CPS.

This experiment is a reproducible perturbation study aligned with the reference
semantic/fuzzy configuration under Reproducibility/. It is supplemental to the
historical latency datasets and does not retroactively alter them.

Perturbations:
- noisy telemetry: Gaussian perturbation of illumination context
- missing telemetry: 30% independent dropout on DT state, command, and lux evidence
- delayed telemetry: +100 ms controlled delivery delay
- spoofed telemetry: canonical PT-DT state mismatch (C0025-style)
- out-of-order telemetry: stale benign event delivered after a newer attack event

Metrics:
- deterministic alert retention (%)
- hybrid alert retention (%)
- mean hybrid risk
- evidence completeness (%)
- injected delay (ms)
- chronological final-state correctness (%)

The out-of-order test deliberately exposes a limitation of arrival-order state handling:
the attack alert is retained, but a stale event delivered last can leave the final stored
state chronologically incorrect unless timestamp-aware ordering/rejection is enforced.
"""

import csv
import random
import statistics
from pathlib import Path

THETA = 0.65
SEED = 42
N = 200

def triangle(x, a, b, c):
    if x < a or x > c:
        return 0.0
    if a == b and x <= b:
        return 1.0
    if b == c and x >= b:
        return 1.0
    if x == b:
        return 1.0
    if x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)

def memberships(x):
    return {
        "low": triangle(x, 0.00, 0.00, 0.50),
        "medium": triangle(x, 0.25, 0.50, 0.75),
        "high": triangle(x, 0.50, 1.00, 1.00),
    }

def fuzzy_security_risk(state_mismatch, command_anomaly, sensor_context_anomaly, steps=501):
    s = memberships(state_mismatch)
    c = memberships(command_anomaly)
    x = memberships(sensor_context_anomaly)

    strengths = {
        "low": min(s["low"], c["low"], x["low"]),
        "medium": max(s["medium"], c["medium"], x["medium"]),
        "high": max(
            s["high"],
            c["high"],
            x["high"],
            min(s["medium"], x["medium"]),
            min(c["medium"], s["medium"]),
        ),
    }

    numerator = 0.0
    denominator = 0.0
    for i in range(steps):
        y = i / (steps - 1)
        out = memberships(y)
        aggregated = max(
            min(strengths["low"], out["low"]),
            min(strengths["medium"], out["medium"]),
            min(strengths["high"], out["high"]),
        )
        numerator += y * aggregated
        denominator += aggregated
    return 0.0 if denominator == 0 else numerator / denominator

def derive_inputs(event):
    pt = event.get("physical_on")
    dt = event.get("dt_on")
    state_mismatch = 0.5 if pt is None or dt is None else (1.0 if pt != dt else 0.0)

    cmd = event.get("command_authorized")
    command_anomaly = 0.5 if cmd is None else (0.0 if cmd else 1.0)

    lux = event.get("lux")
    sensor_context_anomaly = (
        0.5 if lux is None else min(1.0, abs(float(lux) - 80.0) / 80.0)
    )
    return state_mismatch, command_anomaly, sensor_context_anomaly

def deterministic_alert(event):
    pt = event.get("physical_on")
    dt = event.get("dt_on")
    cmd = event.get("command_authorized")
    lux = event.get("lux")

    mismatch = pt is not None and dt is not None and pt != dt
    unauthorised = cmd is False
    logical_physical = dt is True and lux is not None and lux < 30.0
    return bool(mismatch or unauthorised or logical_physical)

ATTACK = {
    "physical_on": False,
    "dt_on": True,
    "command_authorized": False,
    "lux": 20.0,
    "timestamp_ms": 1000,
}

STALE_BENIGN = {
    "physical_on": False,
    "dt_on": False,
    "command_authorized": True,
    "lux": 80.0,
    "timestamp_ms": 900,
}

def run():
    rng = random.Random(SEED)
    rows = []

    for condition in [
        "baseline",
        "noisy",
        "missing",
        "delayed",
        "spoofed",
        "out_of_order",
    ]:
        deterministic = []
        hybrid = []
        risks = []
        completeness = []
        delays = []
        chronological_state = []

        for _ in range(N):
            if condition == "out_of_order":
                sequence = [ATTACK.copy(), STALE_BENIGN.copy()]
                det_any = False
                hybrid_any = False
                max_risk = 0.0
                for event in sequence:
                    det_any = det_any or deterministic_alert(event)
                    r = fuzzy_security_risk(*derive_inputs(event))
                    max_risk = max(max_risk, r)
                    hybrid_any = hybrid_any or (r >= THETA)

                deterministic.append(det_any)
                hybrid.append(hybrid_any)
                risks.append(max_risk)
                completeness.append(100.0)
                delays.append(0.0)
                latest_source_ts = max(e["timestamp_ms"] for e in sequence)
                chronological_state.append(
                    100.0 if sequence[-1]["timestamp_ms"] == latest_source_ts else 0.0
                )
                continue

            event = ATTACK.copy()
            injected_delay = 0.0

            if condition == "noisy":
                event["lux"] = max(0.0, ATTACK["lux"] + rng.gauss(0, 10.0))
            elif condition == "missing":
                for key in ["dt_on", "command_authorized", "lux"]:
                    if rng.random() < 0.30:
                        event.pop(key, None)
            elif condition == "delayed":
                injected_delay = 100.0
                event["arrival_ms"] = event["timestamp_ms"] + injected_delay
            elif condition == "spoofed":
                event["dt_on"] = not event["physical_on"]

            deterministic.append(deterministic_alert(event))
            r = fuzzy_security_risk(*derive_inputs(event))
            hybrid.append(r >= THETA)
            risks.append(r)
            completeness.append(
                100.0
                * sum(k in event for k in ["dt_on", "command_authorized", "lux"])
                / 3.0
            )
            delays.append(injected_delay)
            chronological_state.append(100.0)

        rows.append(
            {
                "condition": condition,
                "n": N,
                "det_alert_retention_pct": round(
                    100.0 * sum(deterministic) / N, 1
                ),
                "hybrid_alert_retention_pct": round(100.0 * sum(hybrid) / N, 1),
                "mean_hybrid_risk": round(statistics.mean(risks), 3),
                "evidence_completeness_pct": round(
                    statistics.mean(completeness), 1
                ),
                "injected_delay_ms": round(statistics.mean(delays), 1),
                "chronological_final_state_pct": round(
                    statistics.mean(chronological_state), 1
                ),
            }
        )

    out = Path(__file__).with_name("telemetry_robustness_results.csv")
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    for row in rows:
        print(row)
    print(f"\nWrote: {out}")

if __name__ == "__main__":
    run()
