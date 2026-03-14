import yaml

params_path = "../config/params.yaml"

with open(params_path, "r") as f:
    params = yaml.safe_load(f)

starting_value = params["gbm"]["init_value"]
drift = params["gbm"]["mu"]
volatility = params["gbm"]["std"]
periods = params["gbm"]["periods"]


