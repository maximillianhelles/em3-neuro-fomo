import yaml
import numpy as np
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "../../config/params.yaml")

def _load_params(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def calc_jdm_values(init_value=100, direction=1, rng=None, **overrides):
    
    if rng is None:
        rng = np.random.default_rng()
    
    # Initialize parameters
    p = _load_params(yaml_path)
    drift = overrides.get("drift", p["jdm"]["mu"])
    volatility = overrides.get("volatility", p["jdm"]["sigma"])
    periods = overrides.get("periods", p["jdm"]["periods"])
    jump = overrides.get("jump", p["jdm"]["mu_jump"])
    std_jump = overrides.get("std_jump", p["jdm"]["sigma_jump"])
    
    # GBM calculation
    shocks = rng.normal(drift, volatility, periods) # No ito correction since mu is already based on ito corrected log returns
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