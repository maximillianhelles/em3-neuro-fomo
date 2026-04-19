# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EEG neuroscience experiment studying Event-Related Potentials (P300 and FRN) in response to financial volatility and counterfactual regret. Participants observe/trade fictional assets while EEG is recorded; price paths are generated via a Jump-Diffusion model (GBM + spikes) calibrated on historical Bitcoin data.

## Setup

```bash
pip install -r requirements.txt
```

Python version is pinned to 3.10.13 via `.python-version`. PsychoPy is required for the display layer but will gracefully print a warning if missing.

## Running the Experiment

```bash
# 1. (Re-)estimate GBM parameters from historical BTC data → updates config/params.yaml
cd analysis/pre && python3 gbm_params.py

# 2. Run the experiment (must be run from the experiment/ directory due to relative imports)
cd experiment && python3 run_exp.py
```

Both scripts use relative paths internally, so they **must** be run from their own directories.

Set `trigger_mode: dummy` in `config/params.yaml` to run without hardware (silent no-op triggers). Set `trigger_mode: hardware` for serial port triggers. Set `fullscr=False` in `run_exp.py` for windowed mode.

On launch, `run_exp.py` prompts for a participant ID (rejects duplicates that already have data) and participant type (`behavioral` = 7 trials/condition, `eeg` = 20 trials/condition, `custom` = manual entry).

## Architecture

**Config** — `config/params.yaml` is the single source of truth for all experiment and model parameters. `config/trial_plans.json` contains pre-generated, seeded trial orderings (position × spike direction) for each block; regenerate with `config/trial_generator.py`.

**Stimuli backend** (`stimuli/backend/jmp_diff_model.py`) — `calc_jdm_values()` generates a single trial's price path: GBM base movement + a directional spike injected at a random point between 10%–90% of the trial. Returns `(values, jump_pct, jump_point)`. Parameters come from `params.yaml` but can be overridden via kwargs.

**Stimuli frontend** (`stimuli/frontend/display.py`) — PsychoPy-based `ExpInterface` class. Key methods: `position_disclosure()` (shows position/capital), `chart_phase()` (renders live chart tick-by-tick at 25ms intervals, handles buy/sell keypresses, sends TTL triggers at spike onset), `sam_rating()` (valence/arousal/regret on 1–9 scale), `fix_cross()` (ITI fixation). Escape key aborts via `ExperimentAborted` exception at any phase.

**Experiment orchestration** (`experiment/`) — `run_exp.py` is the entry point. `blocks.py:run_block()` handles trial-level logic: selects trials from the master plan via `get_participant_plan()`, assigns random tickers, seeds RNG deterministically per trial (`block_offset + trial_num`), and appends behavioral data row-by-row to CSV. `triggers.py` provides `TriggerCode` constants and `get_trigger_sender()` factory (returns `DummyTrigger` or `SerialTrigger`).

**Analysis** (`analysis/pre/gbm_params.py`) — Estimates drift (mu) and volatility (sigma) from historical BTC 5-minute returns and writes them back to `params.yaml`.

## Experimental Design

- 3 blocks: **control** (1 DKK nominal), **low** (50 DKK), **high** (100 DKK)
- 4 conditions per block: Gain (invested + positive spike), Loss (invested + negative spike), FOMO (cash + positive spike), Relief (cash + negative spike)
- Participant actions (buy/sell) can shift their realized condition at spike time
- Behavioral data saved to `data/behavioral_data/{block_id}/{subject_id}_results_block.csv`
- EEG data goes to `data/eeg-data/` (populated externally by recording software)

## TTL Trigger Codes

Defined in `experiment/triggers.py` as `TriggerCode` class constants (1–12). Sent at block start/end, trial start/end, position disclosure, buy/sell actions, positive/negative spikes, and SAM rating onset. The `trigger_mode` config key switches between `dummy` and `hardware`.

## Key Conventions

- All config reads go through `params.yaml`; never hardcode experiment parameters.
- Trial seeds are deterministic: `block_offset + trial_num` ensures reproducibility across runs.
- The chart renders one data point per frame at 25ms intervals (40 fps effective), with a 1s pause on the final frame.
- No test suite exists; verify changes by running with `trigger_mode: dummy` and `fullscr=False`.
