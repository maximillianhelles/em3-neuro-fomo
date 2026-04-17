import numpy as np
import yaml
import os
import pandas as pd

def estimate_gbm_params(series, freq_seconds=60):
    """
    Estimate GBM drift (mu) and volatility (sigma) from a price series.
    """
    if freq_seconds > 60:
        rule = f"{freq_seconds}s"
        series = series.resample(rule).last().dropna()

    log_rets = np.log(series / series.shift(1))

    time_diff = series.index.to_series().diff().dt.total_seconds()
    log_rets = log_rets[time_diff == freq_seconds]

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

    return mu_est, sigma_est, len(results)

base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "../../config/params.yaml")

with open(yaml_path, "r") as f:
    params = yaml.safe_load(f)

data_set = params["jdm"]["data_set"]
freq = params["jdm"]["bar_seconds"]

csv_path = os.path.join(base_dir, "../..", data_set)

print(f"Loading {data_set} ...")
df = pd.read_csv(csv_path)
df["Timestamp"] = pd.to_datetime(df["Timestamp"].astype(float), unit="s")
df = df.set_index("Timestamp").sort_index()
print(f"Loaded {len(df):,} rows, {df.index.min()} → {df.index.max()}")

close = df["Close"]

mu, sigma, n_days = estimate_gbm_params(close, freq_seconds=freq)

params["jdm"]["mu"] = float(mu)
params["jdm"]["sigma"] = float(sigma)

with open(yaml_path, "w") as f:
    yaml.dump(params, f)

print(f"\n Config updated with mu and sigma at {yaml_path}")