HySecTwin Ontology Starter Package

Files:
- hysectwin_saref_ontology.ttl
- hysectwin_instances.ttl
- ditto_json_to_rdf.py
- sample_device.json

Suggested placement:
HybridSec-Digital-Twin-CSP-Modelling/Eclipse-Ditto-Twin Modelling/

Run:
pip install rdflib
python ditto_json_to_rdf.py --input sample_device.json --output device_output.ttl
