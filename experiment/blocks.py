import os
import random
import yaml
import sys
import csv
import json
import numpy as np

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))

from triggers import get_trigger_sender, TriggerCode
from stimuli.backend.jmp_diff_model import calc_jdm_values as jdm

config_path = os.path.join(base_dir, "../config/params.yaml")
trial_plans_path = os.path.join(base_dir, "../config/trial_plans.json")

with open(config_path,"r") as f:
    params = yaml.safe_load(f)

with open(trial_plans_path, "r") as f:
    TRIAL_PLANS = json.load(f)

def get_seed(block_id, trial_num):
    block_offset = {"control": 0, "low": 10000, "high": 20000}
    return block_offset[block_id] + trial_num

def get_participant_plan(master_plan, trials_per_condition):
    """Take the first N trials of each condition from the master plan,
    preserving their original trial numbers so seeds stay aligned."""
    counts = {("ASSET", 1): 0, ("ASSET", -1): 0, ("CASH", 1): 0, ("CASH", -1): 0}
    selected = []
    for i, (position, direction) in enumerate(master_plan, start=1):
        combo = (position, direction)
        if counts[combo] < trials_per_condition:
            selected.append((i, position, direction))
            counts[combo] += 1
        if all(c == trials_per_condition for c in counts.values()):
            break
    return selected

def run_block(interface, subject_id, block_id, trials_per_condition):
    # Determine intial capital
    capital_map = {"control": 1, "low": 50, "high": 100}
    if block_id not in capital_map:
        raise ValueError(f"{block_id} is an invalid block_id")
    capital = capital_map[block_id]

    # Create new dataset
    csv_path = os.path.join(base_dir, f"../data/behavioral_data/{block_id}/{subject_id}_results_block.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    fieldnames = ["participant_id", "block_id", "trial_num", "ticker",
                "position", "direction", "jump_pct", "chart_values", "action_taken", "action_value",
                "final_value", "valence", "arousal", "regret"]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    master_plan = [tuple(t) for t in TRIAL_PLANS[block_id]]
    participant_plan = get_participant_plan(master_plan, trials_per_condition)

    tickers = random.sample(params["exp"]["tickers"], len(participant_plan))

    trigger = get_trigger_sender()
    trigger.send(TriggerCode.BLOCK_START)

    for (trial_num, position, direction), ticker in zip(participant_plan, tickers):
        if position == "ASSET":
            trigger.send(TriggerCode.ASSET)
        else:
            trigger.send(TriggerCode.CASH)

        # Trial information becomes visible to participant
        interface.position_disclosure(position, capital, ticker)

        # Trial begins
        rng = np.random.default_rng(get_seed(block_id, trial_num))
        values, jump, jump_point = jdm(init_value=capital, direction=direction, rng=rng)
        trigger.send(TriggerCode.TRIAL_START)
        action_taken, action_value = interface.chart_phase(values, position, jump, jump_point, trigger)

        # SAM-rating
        trigger.send(TriggerCode.SAM_RATING)
        responses = interface.sam_rating()

        # Append to behavioral data to CSV
        with open(csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow({
                "participant_id": subject_id,
                "block_id": block_id,
                "trial_num": trial_num,
                "ticker": ticker,
                "position": position,
                "direction": direction,
                "jump_pct": jump,
                "chart_values": [round(v, 4) for v in values],
                "action_taken": action_taken,
                "action_value": action_value,
                "final_value": values[-1],
                "valence": responses["valence"],
                "arousal": responses["arousal"],
                "regret": responses["regret"],
            })

        # Fix Cross
        trigger.send(TriggerCode.TRIAL_END)
        interface.fix_cross()
    
    trigger.send(TriggerCode.BLOCK_END)
    print(f"{subject_id} has successfully completed block: {block_id}")