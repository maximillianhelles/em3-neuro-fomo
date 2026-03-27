import os
import random
import yaml
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))

from triggers import get_trigger_sender, TriggerCode
from stimuli.backend.jmp_diff_model import calc_jdm_values as jdm
from stimuli.frontend.display import ExpInterface

config_path = os.path.join(base_dir, "../config/params.yaml")

with open(config_path,"r") as f:
    params = yaml.safe_load(f)

def run_block(block_id, fullscr=False):
    combos = [("ASSET", 1), ("ASSET", -1), ("CASH", 1), ("CASH", -1)]
    all_trials = combos * params["exp"]["trials_per_condition"]
    random.shuffle(all_trials)
    trials, directions = zip(*all_trials)
    tickers = random.sample(params["exp"]["tickers"], len(all_trials))

    capital_map = {"control": 0, "low": 50, "high": 100}
    if block_id not in capital_map:
        raise ValueError(f"{block_id} is an invalid block_id")
    capital = capital_map[block_id]

    trigger = get_trigger_sender()
    block = ExpInterface(fullscr)
    trigger.send(TriggerCode.BLOCK_START)

    for trial, ticker, direction in zip(trials,tickers, directions):
        if trial == "ASSET":
            trigger.send(TriggerCode.POSITION_INVESTED)
        else:
            trigger.send(TriggerCode.POSITION_UNINVESTED)

        # Trial information becomes visible to participant
        block.position_disclosure(trial, capital, ticker)

        # Trial begins
        values, jump, jump_point = jdm(init_value=capital, direction=direction)
        trigger.send(TriggerCode.TRIAL_START)
        block.chart_phase(values, trial, jump, jump_point, trigger)
        # Show SAM-rating screen
        trigger.send(TriggerCode.SAM_RATING)

        # Log trial to CSV logic

        trigger.send(TriggerCode.TRIAL_END)
        block.fix_cross()
    
    trigger.send(TriggerCode.BLOCK_END)

run_block("low")