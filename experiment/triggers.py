import yaml
import os
import serial
try:
    from psychopy import parallel, core
except ImportError:
    print("PsychoPy not found. Running in 'Dummy Mode'.")

base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "../config/params.yaml")

with open(yaml_path, "r") as f:
    params = yaml.safe_load(f)

class TriggerCode:
    BLOCK_START         = 1
    INFO_START          = 2
    TRIAL_START         = 3
    SELL_ACTION         = 4
    BUY_ACTION          = 5
    SPIKE_POSITIVE      = 6
    SPIKE_NEGATIVE      = 7
    TRIAL_END           = 8
    BLOCK_END           = 9
    POSITION_INVESTED   = 10
    POSITION_UNINVESTED = 11
    SAM_RATING          = 12

class DummyTrigger():
    def send(self, code):
        print(f"[TTL] Trigger sent: {code}")

class ParallelPortTrigger():
    def __init__(self):
        try:
            self.port = serial.Serial("COM4", 115200)
            self.port_type = "serial"
        except NotImplementedError:
            self.port = parallel.ParallelPort(0x0378)
            self.port_type = "parallel"
        except:
            self.port_type = None
            print("[TTL] Warning: no port found — triggers will not be sent")
        
        print(f"[TTL] Port type: {self.port_type}")

    def send(self, code):
        if self.port_type == "parallel":
            self.port.setData(code)
            core.wait(0.020)
            self.port.setData(0)
        elif self.port_type == "serial":
            self.port.write(code.to_bytes(1, "big"))
        else:
            print(f"[TTL] No port — trigger {code} not sent")
        
        print(f"[TTL] Trigger sent: {code}")


def get_trigger_sender():
    mode = params["exp"]["trigger_mode"]  
    if mode == "dummy":
        return DummyTrigger()
    elif mode == "parallel":
        return ParallelPortTrigger()
    else:
        raise ValueError(f"Unknown trigger mode: {mode}")