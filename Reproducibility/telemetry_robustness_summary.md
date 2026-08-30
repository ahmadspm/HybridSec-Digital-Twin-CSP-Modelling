# Telemetry robustness experiment

This supplemental experiment addresses robustness of the HySecTwin reasoning pipeline under controlled telemetry perturbations aligned with the smart-lighting CPS and the reference fuzzy configuration.

## Experimental design

- Fixed random seed: `42`
- Trials per condition: `200`
- Hybrid alert threshold: `theta = 0.65`
- Noisy telemetry: Gaussian illumination perturbation, sigma = 10 lux
- Missing telemetry: 30% independent dropout applied to DT state, command-authorisation, and lux evidence
- Delayed telemetry: +100 ms controlled delivery delay
- Spoofed telemetry: PT-DT light-state inconsistency corresponding to the C0025-style condition
- Out-of-order telemetry: a stale benign event (source timestamp 900 ms) is delivered after a newer attack event (source timestamp 1000 ms)

The baseline attack observation represents a light physically OFF while the DT reports ON, an unauthorised command context, and low illumination. The experiment measures retention of the attack alert rather than supervised classification accuracy.

## Results

| Telemetry condition | N | Deterministic alert retained | Hybrid alert retained | Mean hybrid risk | Evidence completeness | Injected delay | Chronological final state |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 200 | 100.0% | 100.0% | 0.834 | 100.0% | 0 ms | 100.0% |
| Noisy | 200 | 100.0% | 100.0% | 0.778 | 100.0% | 0 ms | 100.0% |
| Missing | 200 | 91.0% | 100.0% | 0.731 | 70.5% | 0 ms | 100.0% |
| Delayed | 200 | 100.0% | 100.0% | 0.834 | 100.0% | 100 ms | 100.0% |
| Spoofed | 200 | 100.0% | 100.0% | 0.834 | 100.0% | 0 ms | 100.0% |
| Out-of-order | 200 | 100.0% | 100.0% | 0.834 | 100.0% | 0 ms | 0.0% |

## Interpretation

The controlled replay shows that the attack alert is retained under noisy, delayed, spoofed, and out-of-order delivery in this reference experiment. Under 30% independent evidence dropout, deterministic alert retention falls to 91.0%, whereas hybrid alert retention remains 100.0% because partial evidence is represented as intermediate uncertainty and combined by fuzzy inference.

The out-of-order condition exposes an important limitation: although the attack is detected when the newer malicious observation is processed, arrival-order handling can leave a stale benign event as the final state. The chronological-final-state metric therefore falls to 0% in this deliberately adversarial ordering. This result motivates timestamp-aware stale-event rejection or sequence validation in future full-stack deployment.

## Scope

These results are from a controlled, reproducible perturbation harness based on the documented smart-lighting semantic and reasoning configuration. They supplement, but do not replace or retroactively modify, the historical full-pipeline latency and campaign results in `DT-Dataset-Analysis/`.
