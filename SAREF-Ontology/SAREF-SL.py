from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, Literal

g = Graph()

EX = Namespace("http://example.org/hysectwin#")
SAREF = Namespace("https://saref.etsi.org/core/")

g.bind("", EX)
g.bind("saref", SAREF)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)

# Classes
g.add((EX.LightingDevice, RDF.type, OWL.Class))
g.add((EX.LightingDevice, RDFS.subClassOf, SAREF.Device))
g.add((EX.Sensor, RDF.type, OWL.Class))
g.add((EX.Sensor, RDFS.subClassOf, SAREF.Device))
g.add((EX.Actuator, RDF.type, OWL.Class))
g.add((EX.Actuator, RDFS.subClassOf, SAREF.Device))
g.add((EX.State, RDF.type, OWL.Class))
g.add((EX.Command, RDF.type, OWL.Class))
g.add((EX.Measurement, RDF.type, OWL.Class))

# Properties
g.add((EX.hasState, RDF.type, OWL.ObjectProperty))
g.add((EX.hasState, RDFS.domain, SAREF.Device))
g.add((EX.hasState, RDFS.range, EX.State))

g.add((EX.uniqueId, RDF.type, OWL.DatatypeProperty))
g.add((EX.uniqueId, RDFS.domain, SAREF.Device))
g.add((EX.uniqueId, RDFS.range, XSD.string))

g.add((EX.reachable, RDF.type, OWL.DatatypeProperty))
g.add((EX.reachable, RDFS.domain, SAREF.Device))
g.add((EX.reachable, RDFS.range, XSD.boolean))

g.add((EX.on, RDF.type, OWL.DatatypeProperty))
g.add((EX.on, RDFS.domain, EX.State))
g.add((EX.on, RDFS.range, XSD.boolean))

# Individual
g.add((EX.Device, RDF.type, EX.LightingDevice))
g.add((EX.Device, EX.uniqueId, Literal("04:cd:15:ff:fe:c8:aa:6e-01")))
g.add((EX.Device, EX.reachable, Literal(True)))
g.add((EX.State1, RDF.type, EX.State))
g.add((EX.State1, EX.on, Literal(True)))
g.add((EX.Device, EX.hasState, EX.State1))

g.serialize("hysectwin_saref_ontology.ttl", format="turtle")
print("Ontology saved.")