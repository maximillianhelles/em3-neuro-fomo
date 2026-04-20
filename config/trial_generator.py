# generate_trial_plans.py — run once, commit the output
import random
import json

def generate_master_plan(seed):
    rng = random.Random(seed)
    combos = [("ASSET", 1), ("ASSET", -1), ("CASH", 1), ("CASH", -1)]
    trials = combos * 20
    rng.shuffle(trials)
    return trials

plans = {
    "control": generate_master_plan(seed=1),
    "low":     generate_master_plan(seed=2),
    "high":    generate_master_plan(seed=3),
}

with open("../config/trial_plans.json", "w") as f:
    json.dump(plans, f)