import numpy as np
import yaml
import csv
import os
import pandas as pd

def estimate_gbm_params(prices, timestamps):
    s = pd.Series(prices, index=pd.to_datetime(timestamps))
    log_rets = np.log(s / s.shift(1))
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

######################################################################

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data/financial_data/sp500_1m.csv")
yaml_path = os.path.join(base_dir, "../../config/params.yaml")

with open(data_path, "r") as f:
    snp_1m = list(csv.DictReader(f))

closes = [float(day["close"]) for day in snp_1m]
timestamps = [day["datetime"] for day in snp_1m]

mu, sigma = estimate_gbm_params(closes, timestamps)

with open(yaml_path,"r") as f:
    params = yaml.safe_load(f)

params["jdm"]["mu"] = float(mu)
params["jdm"]["sigma"] = float(sigma)

with open(yaml_path,"w") as f:
    yaml.dump(params, f)