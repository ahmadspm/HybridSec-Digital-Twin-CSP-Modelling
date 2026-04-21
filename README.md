# HySecTwin: Hybrid Reasoning Security Digital Twin for Cyber-Physical Systems

Holmes, D., Mohsin, A., Nepal, S., Sikos, L., Sarker, I. H., & Janicke, H. (2026). HySecTwin: A Knowledge-Driven Digital Twin Framework Augmented with Hybrid Reasoning for Cyber-Physical Systems. Manuscript under review.
<img width="1855" height="712" alt="Hyb-sec-twni-framework (1)" src="https://github.com/user-attachments/assets/da6f44f8-a11b-4bec-b669-47d4bc15057a" />

## Overview

This repository provides the reproducibility package, source code, datasets, scripts, and experimental artifacts for the paper:

**HySecTwin: A Knowledge-Driven Digital Twin Framework Augmented with Hybrid Reasoning for Cyber-Physical Systems**

HySecTwin integrates:
- Cyber-Physical System (CPS) Physical Twin
- Digital Twin (Eclipse Ditto)
- Semantic Modelling (SAREF + RDF Knowledge Graphs)
- Deterministic Rule-Based Reasoning
- Hybrid Fuzzy Reasoning
- MQTT Telemetry Pipelines
- MongoDB / InfluxDB / Grafana Monitoring Stack

The framework enables real-time, explainable, and auditable cybersecurity monitoring for mission-critical CPS environments.

## Quick Start

```bash
git clone https://github.com/ahmadspm/HybridSec-Digital-Twin-CSP-Modelling.git
cd HybridSec-Digital-Twin-CSP-Modelling
pip install -r requirements.txt
docker-compose up -d
setupscript.py


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
