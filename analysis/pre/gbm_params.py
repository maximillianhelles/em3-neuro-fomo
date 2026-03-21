import numpy as np
import yaml
import csv
import os
import pandas as pd

def estimate_gbm_params(series):
    log_rets = np.log(series / series.shift(1))
    grouped = log_rets.groupby(log_rets.index.date)

    results = []
    for date, day_rets in grouped:
        rets = day_rets.dropna()
        mean = rets.mean()
        sigma = rets.std()

        results.append({
            "date": date,
            "mean": mean,
            "std": sigma
        })

    mu_est = np.mean([i["mean"] for i in results])
    sigma_est = np.mean([i["std"] for i in results])

    return mu_est, sigma_est

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data/financial_data/BTCUSD_1m_Binance.csv")
yaml_path = os.path.join(base_dir, "../../config/params.yaml")

df = pd.read_csv(
    "../../data/financial_data/BTCUSD_1m_Binance.csv",
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