import os
import sys
import yaml

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))
config_path = os.path.join(base_dir, "../config/params.yaml")
with open(config_path, "r") as f:
    params = yaml.safe_load(f)

from stimuli.frontend.display import ExpInterface, ExperimentAborted
from blocks import run_block

blocks = params["exp"]["blocks"]

while True:
    subject_id = input("Enter Participant ID: ").strip()
    if not subject_id:
        print("ID cannot be empty.")
        continue
    if any(os.path.exists(os.path.join(base_dir, f"../data/behavioral_data/{block}/{subject_id}_results_block.csv"))
            for block in blocks):
        print(f"Subject ID {subject_id} already has data. Try another.")
        continue
    break

while True:
    participant_type = input("Enter Participant Type (behavioral/eeg/custom): ").strip().lower()
    if participant_type in ("behavioral", "behavioural"):
        trials_per_condition = 7
        break
    elif participant_type == "eeg":
        trials_per_condition = 20
        break
    elif participant_type == "custom":
        while True:
            try:
                trials_per_condition = int(input("Enter an integer: ").strip())
                break
            except ValueError:
                print("That's not an integer. Try again.")
        break
    else:
        print("Invalid type. Enter 'behavioral', 'eeg', or 'custom'.")

exp_interface = ExpInterface(fullscr=False)

try:
    for block in blocks:
        run_block(exp_interface, subject_id, block, trials_per_condition)
except ExperimentAborted as e:
    print(f"\n[ABORTED] {e}")