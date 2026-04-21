
from durable.lang import *
import time
from datetime import datetime

with ruleset('c0012_dragonfly'):
    
    # Unauthorized HMI access (T0801)
    @when_all(m.device == 'HMI', m.activity == 'unauthorized_access')
    def hmi_intrusion(c):
        c.assert_fact({
            'alert': 'HMI unauthorized access detected',
            'campaign': 'C0012',
            'ttp': 'T0801',
            'description': 'Unauthorised access attempt on HMI device.',
            'confidence': 0.95,
            'timestamp': datetime.utcnow().isoformat()
        })

    # Unknown PLC firmware (T0827)
    @when_all(m.device == 'PLC', m.firmware_version == 'unknown')
    def plc_firmware_alert(c):
        c.assert_fact({
            'alert': 'Unknown PLC firmware version detected',
            'campaign': 'C0012',
            'ttp': 'T0827',
            'description': 'PLC firmware version is unknown or unverified.',
            'confidence': 0.9,
            'timestamp': datetime.utcnow().isoformat()
        })

    # Suspicious MODBUS function code (T0850)
    @when_all(m.device == 'Gateway', m.modbus == 'suspicious_function_code')
    def modbus_anomaly(c):
        c.assert_fact({
            'alert': 'Suspicious MODBUS function code',
            'campaign': 'C0012',
            'ttp': 'T0850',
            'description': 'Detected unrecognised or suspicious MODBUS code on gateway.',
            'confidence': 0.88,
            'timestamp': datetime.utcnow().isoformat()
        })

    # Irregular sensor frequency (T0860)
    @when_all(m.device.matches('Sensor.*'), m.frequency == 'irregular')
    def sensor_irregular(c):
        c.assert_fact({
            'alert': 'Sensor reporting irregular frequency',
            'campaign': 'C0012',
            'ttp': 'T0860',
            'description': 'Sensor data showing irregular reporting frequency.',
            'confidence': 0.85,
            'timestamp': datetime.utcnow().isoformat()
        })

    # RTU configuration overwritten (T0846)
    @when_all(m.device == 'RTU', m.config == 'overwritten')
    def rtu_config_change(c):
        c.assert_fact({
            'alert': 'RTU configuration was overwritten',
            'campaign': 'C0012',
            'ttp': 'T0846',
            'description': 'Detected overwrite of RTU configuration.',
            'confidence': 0.9,
            'timestamp': datetime.utcnow().isoformat()
        })

# Start the host
if __name__ == '__main__':
    run_all()

# README:
# Save this as durable_rules_script.py in the appropriate directory.

# Ensure it is executed as part of my rule engine service container (via Docker or local run).

# This ruleset will respond to facts/messages posted that match the simulated C0012 payloads from simulate_c0012_attacks.py.

