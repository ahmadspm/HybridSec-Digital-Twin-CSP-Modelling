# HySecTwin reasoning reproducibility package

This directory consolidates the methodological artefacts needed to reproduce the semantic-to-reasoning workflow.

## Contents

- `hysectwin_fuzzy_reference.fll` — reference FuzzyLite configuration exposing the fuzzy inputs, membership functions, rules, aggregation, defuzzification, and risk output.
- `reasoning_configuration.md` — fixed thresholds, confidence bands, semantic-to-fuzzy mappings, and parameter-selection rationale.
- `reasoning_pipeline_example.py` — executable walkthrough from normalized semantic facts to deterministic and fuzzy security assessment.

The package should be read together with the existing repository artefacts:

- `SAREF-Ontology/SAREF-CPS-ontology.ttl`
- `Eclipse-Ditto-Twin Modelling/hysectwin_ontology_package/hysectwin_saref_ontology.ttl`
- `Eclipse-Ditto-Twin Modelling/hysectwin_ontology_package/hysectwin_instances.ttl`
- `Eclipse-Ditto-Twin Modelling/hysectwin_ontology_package/ditto_json_to_rdf.py`
- `BenchMark/durable_rules_script.py`
- `BenchMark/simulate_c0012_attacks.py`
- `BenchMark/hybrid_engine_performance.py`

## Reproducible reasoning flow

The reference flow is:

`PT/DT observation -> DT JSON -> RDF/SAREF assertions -> normalized fact base -> deterministic durable_rules + fuzzy reasoning -> confidence/risk assessment -> security alert`

The deterministic examples are the executable rules in `BenchMark/durable_rules_script.py`. The fuzzy configuration in this directory provides an explicit reference implementation of the membership functions and thresholds corresponding to the manuscript's uncertainty-aware reasoning description and Figure 3 examples.

