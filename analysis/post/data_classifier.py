from pathlib import Path
import yaml
import pandas as pd
import numpy as np
import ast

# --- LOAD DATA ---
base_dir = Path(__file__).resolve().parent
data_dir = base_dir / "../../data/behavioral_data"
config_path = base_dir / "../../config/params.yaml"

with open(config_path, "r") as f:
    params = yaml.safe_load(f)

blocks = params["exp"]["blocks"]

files = sorted(f for f in data_dir.rglob("*_results_block.csv") if f.parent.name != "excluded")

print(f"Found {len(files)} files")

dfs = [pd.read_csv(file, dtype={"participant_id": str}) for file in files]
master = pd.concat(dfs, ignore_index=True)

master["block_id"] = pd.Categorical(master["block_id"], categories=["control", "low", "high"], ordered=True)
master = master.sort_values(["block_id", "participant_id", "trial_num"]).reset_index(drop=True)

#print(master.head)

# --- INFER COLUMNS & ADD TO DATAFRAME ---
# Intended Condition ('Gain', 'Loss', 'FOMO', 'Relief')
conditions = [
    (master["position"] == "ASSET") & (master["direction"] == 1),
    (master["position"] == "ASSET") & (master["direction"] == -1),
    (master["position"] == "CASH")  & (master["direction"] == 1),
    (master["position"] == "CASH")  & (master["direction"] == -1),
]
choices = ["Gain", "Loss", "FOMO", "Relief"]

master["intended_condition"] = np.select(conditions, choices, default=None)

#print(master["intended_condition"].value_counts())

# Action Kind ('BUY', 'SELL', 'None')
master["action_kind"] = master["action_taken"].apply(
    lambda s: ast.literal_eval(s)[1]  # returns 'BUY', 'SELL', or None
)

# Action Before Spike (True / False)
master["action_before_spike"] = master["action_index"] < master["jump_index"]

# Difference between jump_index and action_index (jump_index as anchor point)
master["action_index"] = master["action_index"].astype("Int64")
master["diff_action_jmp"] = master["action_index"] - master["jump_index"]

# Realized Condition
flip = {"Gain": "FOMO", "FOMO": "Gain", "Loss": "Relief", "Relief": "Loss"}

master["realized_condition"] = np.where(
    master["action_before_spike"],
    master["intended_condition"].map(flip),
    master["intended_condition"]
)

#print(master["realized_condition"].value_counts(dropna=False))
#print(pd.crosstab(master["intended_condition"], master["realized_condition"]))

# --- OUTPUT ---

output_path = base_dir / "../../data/behavioral_data/master_classified.csv"
master.to_csv(output_path, index=False)