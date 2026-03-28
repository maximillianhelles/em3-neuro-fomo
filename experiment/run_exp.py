import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))

from stimuli.frontend.display import ExpInterface, ExperimentAborted
from blocks import run_block

exp_interface = ExpInterface(fullscr=False)
subject_id = "001"
blocks = ["control", "low", "high"]

try:
    for block in blocks:
        run_block(exp_interface, subject_id, block)
except ExperimentAborted as e:
    print(f"\n[ABORTED] {e}")

## Centralize blocks in config