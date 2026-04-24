import os
import sys
import yaml
import csv

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))
sys.path.append(base_dir)

config_path = os.path.join(base_dir, "../config/params.yaml")
with open(config_path, "r") as f:
    params = yaml.safe_load(f)

from stimuli.frontend.display import ExpInterface, ExperimentAborted
from analysis.pre.gbm_params import load_and_window
from blocks import run_block
from triggers import get_trigger_sender

blocks = params["exp"]["blocks"]
def get_exp_type():
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
    return fullscr

def get_subject_id():
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
    return subject_id

def get_trials_per_condition():
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
                        print(f"""Current master plan only allows for a maximum of 
                            {int(len(params["exp"]["tickers"])/4)} trials per condition. Try again.""")
                        continue
                    break
                except ValueError:
                    print("That's not an integer. Try again.")
            break
        else:
            print("Invalid type. Enter 'behavioral', 'eeg', or 'custom'.")
    return participant_type, trials_per_condition

data_set_path = os.path.join(base_dir, "..", params["jdm"]["data_set"])
windows = load_and_window(data_set_path, freq_seconds=params["jdm"]["bar_seconds"])

try:
    fullscr = get_exp_type()
    subject_id = get_subject_id()
    participant_type, trials_per_condition = get_trials_per_condition()
    
    trigger_mode = "hardware" if participant_type == "eeg" else "dummy"
    trigger = get_trigger_sender(mode=trigger_mode)

    exp_interface = ExpInterface(fullscr=fullscr)
    exp_interface.show_instructions()
    run_block(exp_interface, trigger, subject_id, "practice", 1, save_data=False)
    exp_interface.show_practice_end()

    for block in blocks:
        run_block(exp_interface, trigger, subject_id, block, trials_per_condition)

    if participant_type != "eeg":
        results = exp_interface.stimuli_validation_phase(
            windows, subject_id, init_value=100, n_per_condition=10
        )

        validation_csv = os.path.join(base_dir, "../data/stimuli_validation/validation_results.csv")
        os.makedirs(os.path.dirname(validation_csv), exist_ok=True)
        write_header = not os.path.exists(validation_csv)
        with open(validation_csv, "a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["participant_id", "trial", "response", "truth", "correct"])
            for i, (resp, truth, ok) in enumerate(
                zip(results["response"], results["truth"], results["correct"]), start=1
            ):
                writer.writerow([subject_id, i, resp, truth, ok])
        print(f"Validation results → {validation_csv}")

    exp_interface.win.close()

except ExperimentAborted as e:
    print(f"\n[ABORTED] {e}")