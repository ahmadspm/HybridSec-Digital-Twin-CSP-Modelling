import time
import psutil
import json

# Settings
benchmark_phase = "durable_only"  # Comment/Uncomment to run 'durable_rules' only phase
# benchmark_phase = "hybrid"  # Comment/Uncomment to run Hybrid durable_rules/FuzzyLite phase
benchmark_log = []

def log_resource_usage(label):
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    entry = {"label": label, "cpu": cpu, "memory": mem, "timestamp": time.time()}
    benchmark_log.append(entry)
    print(f"[{label}] CPU: {cpu}%, MEM: {mem}%")

def simulate_reasoning_event():
    if benchmark_phase == "durable_only":
        # Simulate Durable_Rules trigger
        payload = {"device": "PLC", "firmware_version": "unknown", "event": "rule_match"}
    else:
        # Simulate FuzzyLite Hybrid trigger
        payload = {"device": "Sensor01", "frequency": "irregular", "event": "fuzzy_rule_match"}
    print("Reasoning event simulated:", payload)
    time.sleep(0.5)  # simulate processing delay
    return payload

def run_benchmark():
    print(f"Starting benchmark in phase: {benchmark_phase}")
    for i in range(5):
        log_resource_usage(f"Pre-event-{i+1}")
        simulate_reasoning_event()
        log_resource_usage(f"Post-event-{i+1}")

    with open(f"benchmark_log_{benchmark_phase}.json", "w") as f:
        json.dump(benchmark_log, f, indent=4)
    print("Benchmark completed and saved.")

if __name__ == "__main__":
    run_benchmark()


# Notes: 
    # Run simulate_c0012_attacks.py from your project root to emulate live MQTT events.

    # Run benchmark_runner.py twice:

    # Once with benchmark_phase = "durable_only"

    # Then change it to "hybrid" to simulate FuzzyLite-enhanced reasoning.
