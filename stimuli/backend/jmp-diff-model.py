import yaml
import numpy as np
import matplotlib.pyplot as plt
import json

params_path = "../../config/params.yaml"

with open(params_path, "r") as f:
    params = yaml.safe_load(f)

s0 = params["gbm"]["init_value"]
drift = params["gbm"]["mu"]
volatility = params["gbm"]["sigma"]
periods = params["gbm"]["periods"]

shocks = np.random.normal(drift, volatility, periods)
values = s0 * np.exp(np.cumsum(shocks))
values = np.insert(values, 0, s0).tolist()

with open("values.json", "w") as f:
    json.dump(values, f)