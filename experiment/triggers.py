import yaml
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "../config/params.yaml")

with open(yaml_path, "r") as f:
    params = yaml.safe_load(f)

class TriggerCode:
    BLOCK_START         = 1
    TRIAL_START         = 2
    SPIKE_POSITIVE      = 3
    SPIKE_NEGATIVE      = 4
    TRIAL_END           = 5
    BLOCK_END           = 6
    POSITION_INVESTED   = 7
    POSITION_UNINVESTED = 8
    SAM_RATING =          9

class TriggerSender:
    def send(self, code):
        raise NotImplementedError

class DummyTrigger(TriggerSender):
    def send(self, code):
        print(f"[TTL] Trigger sent: {code}")

class ParallelPortTrigger(TriggerSender):
    def send(self, code):
        # real hardware code here
        pass

def get_trigger_sender():
    mode = params["experiment"]["trigger_mode"]  
    if mode == "dummy":
        return DummyTrigger()
    elif mode == "parallel":
        return ParallelPortTrigger()
    else:
        raise ValueError(f"Unknown trigger mode: {mode}")