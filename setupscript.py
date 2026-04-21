import subprocess
import time
import os

print("="*60)
print("Launching HySecTwin Reproducibility Framework")
print("="*60)

# Start infrastructure
print("[1/5] Starting Docker services...")
subprocess.run(["docker-compose", "up", "-d"])

time.sleep(10)

# Run Durable Rules engine
print("[2/5] Starting reasoning engine...")
subprocess.Popen(["python", "scripts/durable_rules_script.py"])

time.sleep(3)

# Simulate CPS attacks
print("[3/5] Injecting C0012 attack scenarios...")
subprocess.run(["python", "scripts/simulate_c0012_attacks.py"])

# Run benchmark
print("[4/5] Running benchmark...")
subprocess.run(["python", "scripts/benchmark_runner.py"])

# Run hybrid performance analysis
print("[5/5] Running hybrid reasoning benchmark...")
subprocess.run(["python", "scripts/hybrid_engine_performance.py"])

print("="*60)
print("Reproducibility completed successfully.")
print("Results available in load_testing/")
print("="*60)