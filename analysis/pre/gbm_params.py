import yfinance as yf
import numpy as np
import yaml
import os

def estimate_gbm_params(df):
    log_rets = np.log(df / df.shift(1))
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
yaml_path = os.path.join(base_dir, "../../config/params.yaml")

with open(yaml_path,"r") as f:
    params = yaml.safe_load(f)

ticker = params["jump_gbm"]["ticker"]
period = "7d"
interval = "1m"
df = (yf.download(ticker, period=period, interval=interval))["Close"]
df = df.squeeze()

if df.empty:
    raise ValueError(f"No data returned for ticker: {ticker}. Double-check input parameters")

mu_empirical, sigma_empirical = estimate_gbm_params(df)

params["jump_gbm"]["mu"] = round(float(mu_empirical),6)
params["jump_gbm"]["sigma"] = round(float(sigma_empirical),6)

if interval == "1m":
    params["jump_gbm"]["periods"] = 60*8
elif interval == "5m":
    params["jump_gbm"]["periods"] = 12*8

with open(yaml_path,"w") as f:
    yaml.dump(params, f)