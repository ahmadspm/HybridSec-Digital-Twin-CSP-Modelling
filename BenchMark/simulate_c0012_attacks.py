import time
import json
import paho.mqtt.client as mqtt

# MQTT broker details
broker = "emqx"
port = 1883
topic = "cps/device01/state"

# Sample payloads emulating C0012 (Dragonfly 2.0) behaviours
payloads = [
    {"device": "HMI", "activity": "unauthorized_access", "timestamp": time.time()},
    {"device": "PLC", "firmware_version": "unknown", "timestamp": time.time()},
    {"device": "Gateway", "modbus": "suspicious_function_code", "timestamp": time.time()},
    {"device": "Sensor01", "frequency": "irregular", "timestamp": time.time()},
    {"device": "RTU", "config": "overwritten", "timestamp": time.time()}
]

def publish():
    client = mqtt.Client()
    client.connect(broker, port, 60)
    for payload in payloads:
        msg = json.dumps(payload)
        client.publish(topic, msg)
        print(f"Published: {msg}")
        time.sleep(1)

if __name__ == "__main__":
    publish()

# Notes: 
    # Run simulate_c0012_attacks.py from the project root to emulate live MQTT events.

    # Run benchmark_runner.py twice:

    # Once with benchmark_phase = "durable_only"

    # Then change it to "hybrid" to simulate FuzzyLite-enhanced reasoning.