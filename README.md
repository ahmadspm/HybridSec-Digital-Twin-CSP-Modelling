# HySecTwin: Hybrid Reasoning Security Digital Twin for Cyber-Physical Systems

D. Holmes, A. Mohsin, S. Nepal, L. Sikos, I. H. Sarker, and H. Janicke, “HySecTwin: A Knowledge-Driven Digital Twin Framework Augmented with Hybrid Reasoning for Cyber-Physical Systems,” arXiv preprint arXiv:2605.11682, 2026. Available: https://arxiv.org/abs/2605.11682 [under review].

<img width="1855" height="712" alt="Hyb-sec-twni-framework (1)" src="https://github.com/user-attachments/assets/da6f44f8-a11b-4bec-b669-47d4bc15057a" />

## Overview

This repository provides source code, datasets, scripts, modelling artefacts, and reproducibility material for the paper:

**HySecTwin: A Knowledge-Driven Digital Twin Framework Augmented with Hybrid Reasoning for Cyber-Physical Systems**

## Project Description

HySecTwin is a knowledge-driven cybersecurity framework that integrates Digital Twin technology with semantic modelling and hybrid reasoning to improve the security of Cyber-Physical Systems (CPS). The framework combines real-time device synchronization, SAREF-aligned knowledge graphs, deterministic rules, and fuzzy inference to detect anomalous behavior, unauthorized control actions, and logical–physical inconsistencies. Designed for mission-critical environments, HySecTwin enables explainable, low-latency, and reproducible cybersecurity monitoring for smart industrial and IoT systems.

HySecTwin integrates:
- Cyber-Physical System (CPS) Physical Twin
- Digital Twin (Eclipse Ditto)
- Semantic Modelling (SAREF + RDF Knowledge Graphs)
- Deterministic Rule-Based Reasoning
- Hybrid Fuzzy Reasoning
- MQTT Telemetry Pipelines
- MongoDB / InfluxDB / Grafana Monitoring Stack

## Repository Structure

- `Eclipse-Ditto-Twin Modelling/` — Eclipse Ditto configuration, DT data and JSON-to-RDF transformation artefacts.
- `SAREF-Ontology/` — SAREF-aligned CPS ontology artefacts.
- `BenchMark/` — executable deterministic rule examples, attack simulation and reasoning-performance analysis.
- `DT-Dataset-Analysis/` — historical live-versus-twin latency/throughput measurements and summary data.
- `Reproducibility/` — explicit fuzzy membership functions, thresholds, calibration guidance and an end-to-end reasoning example.

## Reasoning Reproducibility

To make the hybrid reasoning method independently inspectable, the repository includes a dedicated `Reproducibility/` package containing:

- machine-readable FuzzyLite membership functions and fuzzy rules (`hysectwin_fuzzy_reference.fll`);
- the reference decision threshold and confidence bands;
- normalization and calibration procedure (`reasoning_configuration.md`);
- an executable semantic-fact-to-reasoning example (`reasoning_pipeline_example.py`).

The reasoning flow documented there is:

`PT/DT observation -> DT JSON -> RDF/SAREF assertions -> normalized fact base -> deterministic + fuzzy reasoning -> confidence/risk assessment -> security alert`

The deterministic C0012 examples remain in `BenchMark/durable_rules_script.py`, while the ontology schema is available in `SAREF-Ontology/` and `Eclipse-Ditto-Twin Modelling/hysectwin_ontology_package/`.

The historical experimental CSV files are preserved unchanged. The explicit fuzzy reference configuration documents the uncertainty-aware reasoning method for inspection and future reproduction and is not presented as a retroactive regeneration of the historical measurements.

## Quick Reproducibility Check

The reasoning example requires only Python 3:

```bash
git clone https://github.com/ahmadspm/HybridSec-Digital-Twin-CSP-Modelling.git
cd HybridSec-Digital-Twin-CSP-Modelling
python Reproducibility/reasoning_pipeline_example.py
```

For the broader experimental stack, use the relevant Eclipse Ditto, MQTT, MongoDB, InfluxDB, Grafana and benchmark configurations in their respective directories.

## Technology Stack

- Eclipse Ditto
- MQTT
- RDF / SAREF
- Durable Rules
- FuzzyLite
- MongoDB
- InfluxDB
- Grafana
- Docker
- Python

## Citation

```bibtex
@article{hysectwin2026,
  title={HySecTwin: A Knowledge-Driven Digital Twin Framework Augmented with Hybrid Reasoning for Cyber-Physical Systems},
  author={Holmes, David and Mohsin, Ahmad and Nepal, Surya and Sikos, Leslie and Sarker, Iqbal H. and Janicke, Helge},
  year={2026}
}
```

## License

MIT License
