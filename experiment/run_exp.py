import os
import sys
import yaml

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))
sys.path.append(base_dir)

config_path = os.path.join(base_dir, "../config/params.yaml")
with open(config_path, "r") as f:
    params = yaml.safe_load(f)

from stimuli.frontend.display import ExpInterface, ExperimentAborted
from blocks import run_block
from triggers import get_trigger_sender

blocks = params["exp"]["blocks"]

while True:
    exp_type = input("Actual Experiment (Yes/No): ").strip()
    if exp_type.lower() == "yes":
        fullscr = True
        break
    elif exp_type.lower() == "no":
        fullscr = False
        break
    else:
        print("Valid answers are 'Yes' or 'No'.")
        continue

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
        trials_per_condition = params["exp"]["trials_per_condition_behavioral"]
        break
    elif participant_type == "eeg":
        trials_per_condition = params["exp"]["trials_per_condition_eeg"]
        break
    elif participant_type == "custom":
        while True:
            try:
                trials_per_condition = int(input("Enter an integer: ").strip())
                if trials_per_condition > int(len(params["exp"]["tickers"])/4):
                    print(f"""Current master plan only allows for a maximum of {int(len(params["exp"]["tickers"])/4)} trials per condition. Try again.""")
                    continue
                break
            except ValueError:
                print("That's not an integer. Try again.")
        break
    else:
        print("Invalid type. Enter 'behavioral', 'eeg', or 'custom'.")

exp_interface = ExpInterface(fullscr=fullscr)
trigger = get_trigger_sender()

try:
    exp_interface.show_instructions()
    run_block(exp_interface, trigger, subject_id, "practice", 1, save_data=False)
    exp_interface.show_practice_end()
    for block in blocks:
        run_block(exp_interface, trigger, subject_id, block, trials_per_condition)

    exp_interface.win.close()
except ExperimentAborted as e:
    print(f"\n[ABORTED] {e}")