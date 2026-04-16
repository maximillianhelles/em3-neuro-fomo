import os
import sys
import yaml

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))
config_path = os.path.join(base_dir, "../config/params.yaml")
with open(config_path, "r") as f:
    params = yaml.safeload(f)

from stimuli.frontend.display import ExpInterface, ExperimentAborted
from blocks import run_block

exp_interface = ExpInterface(fullscr=False)
subject_id = "001"
blocks = params["exp"]["blocks"]

try:
    for block in blocks:
        run_block(exp_interface, subject_id, block)
except ExperimentAborted as e:
    print(f"\n[ABORTED] {e}")