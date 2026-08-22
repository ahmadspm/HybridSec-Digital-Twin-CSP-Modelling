# HySecTwin reasoning configuration and parameter calibration

## Purpose

This document makes the reference reasoning parameters explicit so that the uncertainty-aware component can be independently inspected and reproduced. It separates three quantities that should not be conflated:

1. deterministic-rule confidence attached to an exact rule match;
2. fuzzy membership degrees used to represent gradual evidence;
3. the final defuzzified `securityRisk` score used for decision support.

## 1. Deterministic rule confidence

The executable C0012 examples in `BenchMark/durable_rules_script.py` use fixed rule confidences:

| Rule condition | ATT&CK ICS technique | Confidence |
|---|---:|---:|
| HMI unauthorized access | T0801 | 0.95 |
| PLC firmware version unknown | T0827 | 0.90 |
| Suspicious MODBUS function code | T0850 | 0.88 |
| Irregular sensor reporting frequency | T0860 | 0.85 |
| RTU configuration overwritten | T0846 | 0.90 |

These values are deterministic alert confidences. They are not fuzzy membership degrees.

## 2. Normalized fuzzy inputs

The reference fuzzy model uses three normalized inputs in `[0,1]`:

- `networkTrafficRate`: deviation from the asset's baseline network-traffic profile;
- `firmwareIntegrityRisk`: uncertainty/risk associated with firmware integrity;
- `commandAnomaly`: deviation of control commands from the expected/authorized pattern.

For a numeric observation `x`, a baseline center `m`, and an allowed baseline deviation `d > 0`, the reference normalization is:

`anomaly(x) = min(1, abs(x-m) / d)`.

This deliberately normalizes heterogeneous telemetry before fuzzy inference. Deployments should estimate `m` and `d` from their own benign baseline rather than treating an absolute packet-rate value as universal across CPS assets.

For categorical evidence, the reference mapping is:

| Semantic state | Normalized risk |
|---|---:|
| verified / authorized / expected | 0.00 |
| uncertain / partially verified / unusual | 0.50 |
| unknown / unverified / unauthorized / suspicious | 1.00 |

## 3. Membership functions

All three inputs use the same transparent triangular partition:

- Low: `Triangle(0.00, 0.00, 0.50)`
- Medium: `Triangle(0.25, 0.50, 0.75)`
- High: `Triangle(0.50, 1.00, 1.00)`

The output `securityRisk` uses the same Low/Medium/High partition. The complete machine-readable configuration is in `hysectwin_fuzzy_reference.fll`.

The overlapping triangles were selected as a parsimonious reference partition: adjacent linguistic states overlap, boundary observations can belong partially to two states, and no discontinuous decision is introduced before defuzzification.

## 4. Inference and defuzzification

The reference FuzzyLite model uses:

- conjunction: Minimum;
- disjunction: Maximum;
- implication: Minimum;
- aggregation: Maximum;
- defuzzification: Centroid (100 divisions).

This is a Mamdani-style reference configuration chosen for transparency and ease of reproduction rather than dataset-specific optimization.

## 5. Decision threshold and confidence bands

The defuzzified output is in `[0,1]`. The reference security decision threshold is:

`theta = 0.65`.

Interpretation:

- `securityRisk < 0.35`: low;
- `0.35 <= securityRisk < 0.65`: medium / review;
- `securityRisk >= 0.65`: high / alert.

The threshold is intentionally documented as a fixed reference operating point. It is not claimed to be a universally optimal threshold or to have been statistically learned from the historical benchmark CSV files.

## 6. Calibration procedure

For reproducible deployment calibration:

1. collect a benign baseline for each numeric telemetry variable;
2. estimate the baseline center `m` and an operationally acceptable deviation `d` for that asset/context;
3. transform raw telemetry to `[0,1]` using the normalization above;
4. apply the fixed membership functions and fuzzy rule base;
5. evaluate the resulting score distribution against labelled benign and attack/review scenarios;
6. retain `theta=0.65` as the reference value or report any deployment-specific threshold separately, together with the validation data and resulting false-positive/false-negative trade-off.

This separation avoids presenting asset-specific raw thresholds as universal CPS constants.

## 7. Relationship to historical experiments

The repository's historical `DT-Dataset-Analysis/` CSV files and existing benchmark scripts are not modified by this reproducibility package. The reference fuzzy configuration makes the paper's uncertainty-aware reasoning method explicit for inspection and future reruns; it should not be interpreted as a retroactive claim that every historical CSV was generated with this newly documented reference file.
