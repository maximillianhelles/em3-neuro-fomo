import os
import random
import yaml
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))

from triggers import get_trigger_sender, TriggerCode
from stimuli.backend.jmp_diff_model import calc_jdm_values as jdm
from stimuli.frontend.display import ExpInterface

yaml_path = os.path.join(base_dir, "../config/params.yaml")

with open(yaml_path,"r") as f:
    params = yaml.safe_load(f)

def run_block(block_id, fullscr=False):
    conds = ["Asset", "Cash"]
    tickers = params["exp"]["tickers"]
    random.shuffle(tickers)
    trials = conds * len(tickers)/len(conds)
    random.shuffle(trials)
    directions = [-1,1]*len(tickers)
    random.shuffle(directions)

    trigger = get_trigger_sender()
    trigger.send(TriggerCode.BLOCK_START)
    block = ExpInterface(fullscr)
    for trial, ticker, direction in zip(trials,tickers, directions):
        if trial == "Asset":
            trigger.send(TriggerCode.POSITION_INVESTED)
        else:
            trigger.send(TriggerCode.POSITION_UNINVESTED)

        capital_map = {"control": 0, "low": 50, "high": 100}
        if block_id not in capital_map:
            raise ValueError(f"{block_id} is an invalid block_id")
        capital = capital_map[block_id]
        # Informing of position logic
        values, jump, jump_point = jdm(init_value=capital, direction=direction)
        trigger.send(TriggerCode.TRIAL_START)
        block.build_chart(values, trial, jump, jump_point, trigger)
        # Show SAM-rating screen
        trigger.send(TriggerCode.SAM_RATING)

        # Log trial to CSV logic

        trigger.send(TriggerCode.TRIAL_END)
        block.fix_cross()
    
    trigger.send(TriggerCode.BLOCK_END)


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
