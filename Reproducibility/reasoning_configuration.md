# HySecTwin reasoning configuration and parameter calibration

## Purpose

This document makes the reference reasoning configuration explicit for inspection and reproduction. The examples are aligned with the smart-lighting CPS used in the article: Zigbee-connected lights, switches/controllers, illumination/temperature/humidity sensors, MQTT telemetry, and Eclipse Ditto twin states. It separates deterministic rule matching from fuzzy membership degrees and the final defuzzified security-risk score.

## 1. Deterministic rule examples aligned with the testbed

This work operationalises campaign-inspired behaviours as observable conditions in the smart-lighting CPS. Deterministic rules therefore operate on light/device state, control commands, configuration/state consistency, reachability, sensor observations, and PT-DT consistency.

| Testbed-observable rule condition | Article mapping | Deterministic outcome |
|---|---|---|
| Remote/unexpected control of a light without an authorised control context | C0012 / unauthorized remote control | Security event |
| Command changes a light state outside the expected control sequence | C0012 / malicious or unexpected command execution | Security event |
| Reported light state is inconsistent with its expected/configured state | C0012 / configuration or state tampering | Security alert |
| Light reports OFF while illumination/context indicates an active-light condition | C0025 / logical-physical state mismatch | Security alert |
| Digital twin reports light ON while the corresponding physical observation indicates OFF | C0025 / DT state spoofing / PT-DT inconsistency | Security alert |

These rules are binary condition-to-alert mappings. No universal deterministic confidence value is assigned here. This avoids treating confidence values from legacy benchmark examples as if they were calibrated probabilities for the smart-lighting testbed.

The older `BenchMark/durable_rules_script.py` contains generic CPS/ICS examples (HMI, PLC, Modbus, RTU). Those examples are retained as legacy benchmark artefacts but are **not** the component model of the smart-lighting physical twin described in the article.

## 2. Normalized fuzzy inputs aligned with the smart-lighting CPS

The reference fuzzy model uses three normalized inputs in `[0,1]` that can be derived from the semantic fact base:

- `stateMismatch`: degree of disagreement between expected/physical context and the reported light or DT state;
- `commandAnomaly`: degree to which a switch/control command deviates from the expected or authorised control pattern;
- `sensorContextAnomaly`: degree to which illumination and related sensor context are inconsistent with the reported/commanded device state.

For a numeric observation `x`, a baseline center `m`, and an allowed baseline deviation `d > 0`, the reference normalization is:

`anomaly(x) = min(1, abs(x-m) / d)`.

For categorical evidence, the reference mapping is:

| Semantic state | Normalized anomaly |
|---|---:|
| consistent / authorised / expected | 0.00 |
| uncertain / partially consistent / unusual | 0.50 |
| inconsistent / unauthorised / suspicious | 1.00 |

This mapping is intentionally asset-relative. Raw illumination, temperature, humidity, or message-rate values should be interpreted against the corresponding device/context baseline rather than treated as universal CPS thresholds.

## 3. Membership functions

All three inputs use the same transparent triangular partition:

- Low: `Triangle(0.00, 0.00, 0.50)`
- Medium: `Triangle(0.25, 0.50, 0.75)`
- High: `Triangle(0.50, 1.00, 1.00)`

The output `securityRisk` uses the same Low/Medium/High partition. The complete machine-readable reference configuration is in `hysectwin_fuzzy_reference.fll`.

The overlapping triangles provide a parsimonious representation of gradual evidence: adjacent linguistic states overlap and boundary observations can belong partially to two states before defuzzification.

## 4. Inference and defuzzification

The reference FuzzyLite model uses:

- conjunction: Minimum;
- disjunction: Maximum;
- implication: Minimum;
- aggregation: Maximum;
- defuzzification: Centroid (100 divisions).

This is a Mamdani-style reference configuration chosen for transparency and reproducibility rather than dataset-specific optimisation.

## 5. Decision threshold and confidence bands

The defuzzified output is in `[0,1]`. The documented reference operating threshold is:

`theta = 0.65`.

Interpretation:

- `securityRisk < 0.35`: low;
- `0.35 <= securityRisk < 0.65`: medium / review;
- `securityRisk >= 0.65`: high / alert.

These values document a reproducible reference configuration. They are not claimed to be universally optimal or statistically learned from the historical benchmark CSV files.

## 6. Calibration procedure

For deployment-specific calibration:

1. collect nominal smart-lighting observations for relevant device states, commands, and sensor context;
2. establish expected PT-DT state relationships and authorised control patterns;
3. estimate baseline centers and acceptable deviations for numeric sensor/context variables;
4. transform observed deviations to `[0,1]` using the normalization above;
5. apply the fixed membership functions and fuzzy rule base;
6. validate the score distribution using nominal, malicious, and ambiguous scenarios;
7. retain `theta=0.65` as the documented reference value or report any deployment-specific threshold separately with its validation evidence.

This keeps calibration tied to observable behaviour of the implemented testbed and avoids introducing PLC/HMI/RTU-specific assumptions that are absent from the physical twin.

## 7. Reasoning pipeline

The reproducible reasoning flow is:

`smart-lighting PT observation -> MQTT/DT state -> SAREF-aligned RDF assertions -> normalized fact base -> deterministic rule matching + fuzzy inference -> securityRisk/confidence -> explainable security alert`

Representative facts include light ON/OFF state, brightness, reachability, switch/control actions, illumination context, sensor observations, and PT-DT state consistency.

## 8. Relationship to historical experiments

 This reproducibility package documents a testbed-aligned reference reasoning configuration for inspection and future reruns; it does not retroactively claim that every historical CSV was generated with this newly documented reference configuration.
