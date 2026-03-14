import yfinance as yf
import numpy as np
import yaml
import os

def get_stock_data(ticker_symbol):
    df = (yf.download(ticker_symbol, period="60d", interval="5m"))["Close"]

    if df.empty:
        raise ValueError(f"No data returned for ticker: {ticker_symbol}. Double-check symbol")
    
    df["log_ret"] = np.log(df / df.shift(1))

    grouped = df.groupby(df.index.date)

    results = []
    for date, day_df in grouped:
        five_min_returns = day_df["log_ret"].dropna()
        if len(five_min_returns) < 78:
            continue
        mean = five_min_returns.mean()
        sigma = five_min_returns.std()

        results.append({
            "date": date,
            "mean": mean,
            "std": sigma
        })

    mu_est = np.mean([i["mean"] for i in results])
    sigma_est = np.mean([i["std"] for i in results])

    return mu_est, sigma_est

base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "../../config/params.yaml")

with open(yaml_path,"r") as f:
    params = yaml.safe_load(f)


ticker = params["gbm"]["ticker"]
mu, std = get_stock_data(ticker)

params["gbm"]["mu"] = round(float(mu),6)
params["gbm"]["sigma"] = round(float(std),6)

with open(yaml_path,"w") as f:
    yaml.dump(params, f)
