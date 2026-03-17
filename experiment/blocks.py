import os
import random
import yaml
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))

from triggers import get_trigger_sender, TriggerCode
from stimuli.backend.jmp_diff_model import calc_jdm_values as jdm

yaml_path = os.path.join(base_dir, "../config/params.yaml")

with open(yaml_path,"r") as f:
    params = yaml.safe_load(f)

def run_block(block_id):
    conds = ["A","B","C","D"]
    trials = conds * params["exp"]["trials_per_condition"]
    random.shuffle(trials)

    trigger = get_trigger_sender()
    
    for trial in trials:
        trigger.send(TriggerCode.TRIAL_START)
        # Position prompt logic via Psychopy - need to create in /stimuli/frontend using a class
        position = "invested" if trial in ["A", "C"] else "uninvested"
        if position == "invested":
            trigger.send(TriggerCode.POSITION_INVESTED)
        else:
            trigger.send(TriggerCode.POSITION_UNINVESTED)

        capital_map = {0: 0, 1: 50, 2: 100}
        if block_id not in capital_map:
            raise ValueError(f"{block_id} is an invalid block_id")
        capital = capital_map[block_id]

        values, jump, jump_point = jdm(init_value=capital) if trial in ["A", "B"] else jdm(init_value=capital, direction=-1)
        for i in range(len(values)):
            if i == jump_point:
                if jump > 0:
                    trigger.send(TriggerCode.SPIKE_POSITIVE)
                else:
                    trigger.send(TriggerCode.SPIKE_NEGATIVE)
            #### Build chart in psychopy window
            # perhaps make class of exp in another stimuli/frontend as a baseline and then append to coordinate system ####
        # Show SAM-rating screen
        trigger.send(TriggerCode.SAM_RATING)
        
        # Log trial to CSV logic

        trigger.send(TriggerCode.TRIAL_END)

        # Show fixation cross in frontend

