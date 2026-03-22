import numpy as np
import yaml
import csv
import os
import pandas as pd

def estimate_gbm_params(series):
    log_rets = np.log(series / series.shift(1))
    
    # Drop any return where the time gap is more than 1 minute
    time_diff = series.index.to_series().diff().dt.total_seconds()
    log_rets = log_rets[time_diff == 60]

    grouped = log_rets.groupby(log_rets.index.date)

    results = []
    for date, day_rets in grouped:
        day_rets = day_rets.dropna()
        if len(day_rets) < 2:
            continue
        results.append({
            "date": date,
            "mean": day_rets.mean(),
            "std": day_rets.std()
        })

    mu_est = np.mean([i["mean"] for i in results])
    sigma_est = np.mean([i["std"] for i in results])

    return mu_est, sigma_est

base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "../../config/params.yaml")

df = pd.read_csv(
    "../../data/financial_data/NASDAQ100_1m_clean.csv",
    parse_dates=["Open time"],
    index_col="Open time"
)

close = df["Close"]
mu, sigma = estimate_gbm_params(close)

with open(yaml_path,"r") as f:
    params = yaml.safe_load(f)

params["jdm"]["mu"] = float(mu)
params["jdm"]["sigma"] = float(sigma)

with open(yaml_path,"w") as f:
    yaml.dump(params, f)