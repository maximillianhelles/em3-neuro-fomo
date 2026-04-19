import yaml
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "../config/params.yaml")

with open(yaml_path, "r") as f:
    params = yaml.safe_load(f)

class TriggerCode:
    BLOCK_START         = 1
    INFO_START          = 2
    TRIAL_START         = 3
    ASSET               = 4
    CASH                = 5
    SELL_ACTION         = 6
    BUY_ACTION          = 7
    SPIKE_POSITIVE      = 8
    SPIKE_NEGATIVE      = 9
    TRIAL_END           = 10
    BLOCK_END           = 11
    SAM_RATING          = 12

class DummyTrigger:
    def send(self, code):
        print(f"[TTL] Trigger sent: {code}")


class SerialTrigger:
    def __init__(self, port_name, baudrate=115200):
        import serial
        self.port = serial.Serial(port_name, baudrate)
        print(f"[TTL] Serial port initialized at {port_name}")

    def send(self, code=1):
        self.port.write(code.to_bytes(1, "big"))
        print(f"[TTL] Trigger sent: {code}")


def get_trigger_sender():
    mode = params["exp"]["trigger_mode"]

    if mode == "dummy":
        return DummyTrigger()

    if mode == "hardware":
        serial_port = params["exp"]["serial_port"]
        return SerialTrigger(serial_port)

    raise ValueError(f"Unknown trigger mode: {mode!r} (expected 'dummy' or 'hardware')")