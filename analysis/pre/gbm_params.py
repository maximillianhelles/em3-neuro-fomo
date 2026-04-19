import numpy as np
import yaml
import os
import pandas as pd

def estimate_gbm_params(series, freq_seconds=60):
    if freq_seconds > 60:
        series = series.resample(f"{freq_seconds}s").last().dropna()

    log_rets = np.log(series / series.shift(1)).dropna()

    if len(log_rets) < 2:
        raise ValueError(f"Only {len(log_rets)} valid returns; cannot estimate.")

    mu_est = log_rets.mean()
    sigma_est = log_rets.std(ddof=1)

    return mu_est, sigma_est, len(log_rets)

base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "../../config/params.yaml")

with open(yaml_path,"r") as f:
    params = yaml.safe_load(f)

data_set = params["jdm"]["data_set"]

print(f"Loading data_set at {yaml_path}")

df = pd.read_csv(
    os.path.join(base_dir, "../..", data_set),
    parse_dates=["Open time"],
    index_col="Open time"
)

close_1m = df["Close"]
close_5m = close_1m.resample("5min").last().dropna()

mu, sigma, n = estimate_gbm_params(close_5m, freq_seconds=params["jdm"]["bar_seconds"])

print(f"Estimated from {n:,} 5-min returns.")

params["jdm"]["mu"] = float(mu)
params["jdm"]["sigma"] = float(sigma)

print(f"Writing drift={round(mu,7)} and volatility={round(sigma,5)} to config file.")

with open(yaml_path,"w") as f:
    yaml.dump(params, f)

print("Written to params.yaml successfully")