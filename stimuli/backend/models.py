import yaml
import json
import numpy as np
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, "../.."))

from analysis.pre.gbm_params import load_and_window

yaml_path = os.path.join(base_dir, "../../config/params.yaml")

def _load_jdm_params():
    with open(yaml_path, "r") as f:
        params = yaml.safe_load(f)["jdm"]

    dist_path = os.path.join(base_dir, "../..", params["distributions_file"])
    with open(dist_path, "r") as f:
        distributions = json.load(f)

    params["mu_distribution"] = distributions["mu"]
    params["sigma_distribution"] = distributions["sigma"]
    return params

def calc_jdm_values(init_value=100, direction=1, rng=None, **overrides):
    if rng is None:
        rng = np.random.default_rng()
    
    # Initialize parameters
    p = _load_jdm_params()
    periods = overrides.get("periods", p["periods"])
    jump = overrides.get("jump", p["mu_jump"])
    std_jump = overrides.get("std_jump", p["sigma_jump"])

    idx = int(rng.integers(len(p["mu_distribution"])))
    drift = overrides.get("drift", p["mu_distribution"][idx])
    volatility = overrides.get("volatility", p["sigma_distribution"][idx])

    # GBM calculation
    shocks = rng.normal(drift, volatility, periods)
    gbm_values = init_value * np.exp(np.cumsum(shocks))
    gbm_values = np.insert(gbm_values, 0, init_value).tolist()

    # Intraday spike
    jump_point = int(rng.integers(periods//10, periods - periods//10)) # ensures 10% margin for start and end
    value = gbm_values[jump_point]
    pct_jump = rng.normal(jump, std_jump)
    value *= 1+direction*pct_jump

    # Update GBM values 
    pre_values = gbm_values[:jump_point]
    remaining_shocks = shocks[jump_point:]
    pre_values.append(value)
    post_values = value * np.exp(np.cumsum(remaining_shocks))
    total_values = pre_values + post_values.tolist()

    return total_values, direction*pct_jump, jump_point

def get_gbm_segment(init_value=100):
    p = _load_jdm_params()
    periods = p["periods"]

    idx = np.random.randint(len(p["mu_distribution"]))
    drift = p["mu_distribution"][idx]
    volatility = p["sigma_distribution"][idx]

    shocks = np.random.normal(drift, volatility, periods)
    gbm_values = init_value * np.exp(np.cumsum(shocks))
    
    return np.insert(gbm_values, 0, init_value).tolist()

def get_btc_segment(windows, init_value=100):
    windows = np.asarray(windows)
    idx = np.random.randint(len(windows))
    prices = windows[idx]
    log_rets = np.log(prices[1:] / prices[:-1])
    segment = init_value * np.exp(np.cumsum(log_rets))
    return np.insert(segment, 0, init_value).tolist()

# data_set_path = os.path.join(base_dir, "../..", _load_jdm_params()["data_set"])
# windows = load_and_window(data_set_path, freq_seconds=300)
