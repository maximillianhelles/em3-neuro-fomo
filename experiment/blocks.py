import os
import random
import yaml
import sys
import csv

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))

from triggers import get_trigger_sender, TriggerCode
from stimuli.backend.jmp_diff_model import calc_jdm_values as jdm

config_path = os.path.join(base_dir, "../config/params.yaml")

with open(config_path,"r") as f:
    params = yaml.safe_load(f)

def run_block(interface, subject_id, block_id):
    # Determine intial capital
    capital_map = {"control": 1, "low": 50, "high": 100}
    if block_id not in capital_map:
        raise ValueError(f"{block_id} is an invalid block_id")
    capital = capital_map[block_id]

    # Create new dataset
    csv_path = os.path.join(base_dir, f"../data/behavioral_data/{block_id}/{subject_id}_results_block.csv")
    
    fieldnames = ["participant_id", "block_id", "trial_num", "ticker",
                "position", "direction", "chart_values", "action_taken", "action_value",
                "final_value", "valence", "arousal", "regret"]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    # Randomize trials
    combos = [("ASSET", 1), ("ASSET", -1), ("CASH", 1), ("CASH", -1)]
    all_trials = combos * params["exp"]["trials_per_condition"]
    random.shuffle(all_trials)
    trials, directions = zip(*all_trials)
    tickers = random.sample(params["exp"]["tickers"], len(all_trials))
    trial_nums = range(1, len(all_trials)+1)

    trigger = get_trigger_sender()
    trigger.send(TriggerCode.BLOCK_START)

    for trial, ticker, direction, trial_num in zip(trials, tickers, directions, trial_nums):
        if trial == "ASSET":
            trigger.send(TriggerCode.ASSET)
        else:
            trigger.send(TriggerCode.CASH)

        # Trial information becomes visible to participant
        interface.position_disclosure(trial, capital, ticker)

        # Trial begins
        values, jump, jump_point = jdm(init_value=capital, direction=direction)
        trigger.send(TriggerCode.TRIAL_START)
        action_taken, action_value = interface.chart_phase(values, trial, jump, jump_point, trigger)

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
                "position": trial,
                "direction": direction,
                "chart_values": [round(v, 4) for v in values],
                "jump_pct": jump,
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
    print(f"{subject_id} has succesfully completed block: {block_id}")