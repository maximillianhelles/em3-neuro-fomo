import os
import random
import yaml
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))

from triggers import get_trigger_sender, TriggerCode
from stimuli.backend.jmp_diff_model import calc_jdm_values as jdm
from stimuli.frontend.display import MainExpInterface

yaml_path = os.path.join(base_dir, "../config/params.yaml")

with open(yaml_path,"r") as f:
    params = yaml.safe_load(f)

def run_block(block_id):
    conds = ["A","B","C","D"]
    trials = conds * params["exp"]["trials_per_condition"]
    random.shuffle(trials)

    trigger = get_trigger_sender()
    
    block = MainExpInterface()
    for trial in trials:
        trigger.send(TriggerCode.TRIAL_START)
        # Position choice logic via Psychopy - need to create in /stimuli/frontend using a class
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
        block.build_chart(values, position, jump, jump_point, trigger)
        # Show SAM-rating screen
        trigger.send(TriggerCode.SAM_RATING)
        # Compare performance of trial to what could have been

        # Log trial to CSV logic

        trigger.send(TriggerCode.TRIAL_END)
        block.fix_cross()


##### TRIAL FLOW #####
# 1. Choose between two masked options. Position randomized. First leads to invested in stock, second leads to cash position.
# 2. After choice, let participant know of the consequence
# 3. Run main trial (not to scale):
# ┌─────────────────┬──────────────────────────┬──────────────────────────────┐
# │                 │                          │                              │
# │   GBM Chart     │  Your cash / Portfolio   │  What if Cash / Portfolio    │
# │                 │                          │                              │
# └─────────────────┴──────────────────────────┴──────────────────────────────┘
# 4. SAM Rating 
# 6. 10s fixation cross to reset
