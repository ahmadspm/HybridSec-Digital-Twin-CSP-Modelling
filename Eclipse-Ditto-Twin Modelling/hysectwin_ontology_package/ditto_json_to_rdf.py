from __future__ import annotations
import argparse, json
from pathlib import Path
from rdflib import Graph, Literal, Namespace, RDF, RDFS, XSD

EX = Namespace("http://example.org/hysectwin#")

def add_if_value(graph: Graph, subj, pred, value, datatype=None):
    if value is None:
        return
    graph.add((subj, pred, Literal(value, datatype=datatype) if datatype else Literal(value)))

def build_graph_from_ditto(payload: dict) -> Graph:
    graph = Graph()
    graph.bind("", EX)

    thing_id = payload.get("thingId") or payload.get("id") or "device_unknown"
    safe_thing = thing_id.replace("/", "_").replace(":", "_").replace("-", "_")
    device_uri = EX[f"Device_{safe_thing}"]
    sensor_uri = EX[f"Sensor_{safe_thing}"]
    actuator_uri = EX[f"Actuator_{safe_thing}"]
    state_uri = EX[f"State_{safe_thing}"]
    command_uri = EX[f"Command_{safe_thing}"]
    measurement_uri = EX[f"Measurement_{safe_thing}"]

    for uri, cls in [
        (device_uri, EX.LightingDevice), (sensor_uri, EX.Sensor), (actuator_uri, EX.Actuator),
        (state_uri, EX.State), (command_uri, EX.Command), (measurement_uri, EX.Measurement)
    ]:
        graph.add((uri, RDF.type, cls))

    for pred, obj in [
        (EX.hasSensor, sensor_uri), (EX.hasActuator, actuator_uri), (EX.hasState, state_uri),
        (EX.hasCommand, command_uri), (EX.hasMeasurement, measurement_uri)
    ]:
        graph.add((device_uri, pred, obj))
    graph.add((measurement_uri, EX.relatesToDevice, device_uri))

    attrs = payload.get("attributes", {})
    features = payload.get("features", {})
    light_block, state_block = {}, {}
    lights = features.get("lights", {})
    if isinstance(lights, dict) and lights:
        first_key = next(iter(lights.keys()))
        light_block = lights[first_key] if isinstance(lights[first_key], dict) else {}
        state_block = light_block.get("state", {}) if isinstance(light_block.get("state", {}), dict) else {}
    else:
        light_block = features if isinstance(features, dict) else {}
        state_block = light_block.get("state", {}) if isinstance(light_block.get("state", {}), dict) else {}

    add_if_value(graph, device_uri, EX.uniqueId, light_block.get("uniqueid") or payload.get("uniqueId"), XSD.string)
    add_if_value(graph, device_uri, EX.lastSeen, light_block.get("lastseen"), XSD.dateTime)
    add_if_value(graph, device_uri, EX.etag, light_block.get("etag"), XSD.string)
    add_if_value(graph, device_uri, EX.manufacturerName, light_block.get("manufacturername"), XSD.string)
    add_if_value(graph, device_uri, EX.deviceType, light_block.get("type"), XSD.string)
    add_if_value(graph, device_uri, EX.ctmax, light_block.get("ctmax"), XSD.integer)
    add_if_value(graph, device_uri, EX.colorCapabilities, light_block.get("colorcapabilities"), XSD.integer)
    add_if_value(graph, device_uri, EX.reachable, state_block.get("reachable"), XSD.boolean)
    add_if_value(graph, state_uri, EX.on, state_block.get("on"), XSD.boolean)
    add_if_value(graph, state_uri, EX.alert, state_block.get("alert"), XSD.string)
    add_if_value(graph, state_uri, EX.colorMode, state_block.get("colormode"), XSD.string)
    add_if_value(graph, state_uri, EX.ct, state_block.get("ct"), XSD.integer)
    add_if_value(graph, measurement_uri, EX.brightness, state_block.get("bri"), XSD.integer)

    telemetry = payload.get("telemetry", {})
    add_if_value(graph, measurement_uri, EX.temperature, telemetry.get("temperature"), XSD.decimal)
    add_if_value(graph, measurement_uri, EX.humidity, telemetry.get("humidity"), XSD.decimal)
    add_if_value(graph, measurement_uri, EX.networkTrafficPps, telemetry.get("network_traffic_pps"), XSD.integer)
    add_if_value(graph, measurement_uri, EX.confidenceScore, telemetry.get("confidence_score"), XSD.decimal)

    command = payload.get("command", {})
    add_if_value(graph, command_uri, EX.commandName, command.get("name"), XSD.string)
    add_if_value(graph, command_uri, EX.commandSource, command.get("source"), XSD.string)

    if "project" in attrs:
        graph.add((device_uri, RDFS.label, Literal(f"{attrs['project']} - {thing_id}")))
    return graph

def main():
    parser = argparse.ArgumentParser(description="Convert Ditto JSON to RDF/Turtle.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    graph = build_graph_from_ditto(payload)
    graph.serialize(destination=args.output, format="turtle")
    print(f"Saved Turtle output to {args.output}")

if __name__ == "__main__":
    main()
