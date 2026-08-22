#!/usr/bin/env python3
"""Minimal HySecTwin semantic-to-reasoning reproducibility example.

No external services are required. The script demonstrates how normalized facts
corresponding to ontology/DT observations can be evaluated by an exact rule and
by the documented fuzzy reference model.
"""

THETA = 0.65


def triangle(x, a, b, c):
    """Triangular/shoulder membership compatible with the reference .fll file."""
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


def normalize_numeric(x, baseline_center, allowed_deviation):
    if allowed_deviation <= 0:
        raise ValueError("allowed_deviation must be > 0")
    return min(1.0, abs(x - baseline_center) / allowed_deviation)


def fuzzy_security_risk(network_risk, firmware_risk, command_risk, steps=1001):
    """Mamdani min/max inference with centroid defuzzification."""
    n = memberships(network_risk)
    f = memberships(firmware_risk)
    c = memberships(command_risk)

    strengths = {
        "low": min(n["low"], f["low"], c["low"]),
        "medium": max(n["medium"], f["medium"], c["medium"]),
        "high": max(
            n["high"],
            f["high"],
            c["high"],
            min(f["medium"], c["medium"]),
        ),
    }

    numerator = 0.0
    denominator = 0.0
    for i in range(steps):
        x = i / (steps - 1)
        out = memberships(x)
        aggregated = max(
            min(strengths["low"], out["low"]),
            min(strengths["medium"], out["medium"]),
            min(strengths["high"], out["high"]),
        )
        numerator += x * aggregated
        denominator += aggregated
    return 0.0 if denominator == 0 else numerator / denominator


def deterministic_reasoning(facts):
    """Mirror selected executable examples from BenchMark/durable_rules_script.py."""
    if facts.get("device") == "HMI" and facts.get("activity") == "unauthorized_access":
        return {"ttp": "T0801", "confidence": 0.95, "alert": "HMI unauthorized access detected"}
    if facts.get("device") == "PLC" and facts.get("firmware_version") == "unknown":
        return {"ttp": "T0827", "confidence": 0.90, "alert": "Unknown PLC firmware version detected"}
    if facts.get("device") == "Gateway" and facts.get("modbus") == "suspicious_function_code":
        return {"ttp": "T0850", "confidence": 0.88, "alert": "Suspicious MODBUS function code"}
    return None


def main():
    # Example normalized fact base derived from DT/semantic observations.
    facts = {
        "device": "PLC",
        "firmware_version": "unknown",
        "network_pps": 760,
        "baseline_network_pps": 500,
        "allowed_network_deviation_pps": 400,
        "command_state": "unusual",
    }

    exact_alert = deterministic_reasoning(facts)

    network_risk = normalize_numeric(
        facts["network_pps"],
        facts["baseline_network_pps"],
        facts["allowed_network_deviation_pps"],
    )
    firmware_risk = 1.0 if facts["firmware_version"] == "unknown" else 0.0
    command_risk = {"expected": 0.0, "unusual": 0.5, "suspicious": 1.0}[facts["command_state"]]

    risk = fuzzy_security_risk(network_risk, firmware_risk, command_risk)

    print("HySecTwin reproducibility example")
    print(f"normalized network risk : {network_risk:.3f}")
    print(f"firmware integrity risk : {firmware_risk:.3f}")
    print(f"command anomaly risk    : {command_risk:.3f}")
    print(f"fuzzy security risk     : {risk:.3f}")
    print(f"decision threshold      : {THETA:.2f}")
    print(f"fuzzy alert             : {risk >= THETA}")
    print(f"deterministic alert     : {exact_alert}")


if __name__ == "__main__":
    main()
