import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, ".."))

from stimuli.frontend.display import ExpInterface
from blocks import run_block

exp_interface = ExpInterface(fullscr=False)
subject_id = "001"
blocks = ["control", "low", "high"]

for block in blocks:
    run_block(exp_interface, subject_id, block)

## Centralize blocks in config