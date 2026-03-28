# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EEG neuroscience experiment studying Event-Related Potentials (P300 and FRN) in response to financial volatility and counterfactual regret. Participants observe/trade fictional assets while EEG is recorded; price paths are generated via a Jump-Diffusion model (GBM + spikes) calibrated on historical Bitcoin data.

## Setup

```bash
pip install -r requirements.txt
```

Python version is pinned to 3.10.13 via `.python-version`.

## Running the Experiment

```bash
# 1. (Re-)estimate GBM parameters from historical BTC data → updates config/params.yaml
python3 analysis/pre/gbm_params.py

# 2. Run the experiment (must be run from the experiment/ directory)
cd experiment
python3 run_exp.py
```

Set `trigger_mode: dummy` in `config/params.yaml` to run without a parallel port (hardware-free testing). Set `fullscr=False` in `run_exp.py` for windowed mode.

## Architecture

The project has four layers:

**Config** — `config/params.yaml` is the single source of truth for all experiment and model parameters (trial counts, ITI duration, key bindings, JDM parameters, asset tickers).

**Stimuli backend** (`stimuli/backend/`) — `jmp_diff_model.py` generates asset price paths using the Jump-Diffusion model. `hist_data_processing.py` parses historical CSV data. `gbm_params.py` estimates drift (mu) and volatility (sigma) and writes them back to `params.yaml`.

**Stimuli frontend** (`stimuli/frontend/display.py`) — PsychoPy-based `ExpInterface` class that renders the live chart, real-time portfolio values (actual + counterfactual), position disclosure screen, and SAM (Self-Assessment Manikin) ratings.

**Experiment orchestration** (`experiment/`) — `run_exp.py` is the entry point; it instantiates `ExpInterface` and calls `run_block()` for each of the three blocks (control/low/high). `blocks.py` handles trial-level logic: randomization of conditions, capturing buy/sell keypresses, and writing behavioral data to CSV. `triggers.py` sends TTL codes via parallel port (or no-ops in dummy mode) for EEG time-locking.

## Experimental Design

- 3 blocks: **control** (no money), **low** (50 DKK), **high** (100 DKK)
- 40 trials/block, 4 conditions: Gain (invested + positive spike), Loss (invested + negative spike), FOMO (cash + positive spike), Relief (cash + negative spike)
- Trial flow: position disclosure → JDM chart with live buy/sell → SAM rating → 5s fixation cross
- Behavioral data saved to `data/behavioral_data/{block_id}/{subject_id}_results_block.csv`
- EEG data goes to `data/eeg-data/` (populated externally by recording software)

## TTL Trigger Codes

Trigger codes are sent in `triggers.py` at spike onset and other key events to time-lock EEG epochs. The `trigger_mode` config key switches between `parallel` (real hardware) and `dummy` (silent no-op).
