import os
import yaml # læser params.yaml
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd #til csv

#sti til params.yaml
base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "config/params.yaml")

with open(yaml_path, "r") as f:
    params = yaml.safe_load(f) # Læs hele yaml som dict

drift = params["jdm"]["mu"]
sigma = params["jdm"]["sigma"]
periods = params["jdm"]["periods"]


def calc_gbm_values(init_value, periods, drift, volatility):
    """Pure GBM without jump - for validation"""
    np.random.seed(42)
    shocks = np.random.normal(drift, volatility, periods)
    gbm_values = init_value * np.exp(np.cumsum(shocks))
    gbm_values = np.insert(gbm_values, 0, init_value)
    return gbm_values.tolist()


def calc_jdm_values(init_value, periods, drift, volatility, direction=1):
    """GBM with jump (for experiment)"""
    np.random.seed(42)
    shocks = np.random.normal(drift, volatility, periods)
    gbm_values = init_value * np.exp(np.cumsum(shocks))
    gbm_values = np.insert(gbm_values, 0, init_value)

    jump_point = np.random.randint(int(periods*0.1), int(periods*0.9))
    value = gbm_values[jump_point]
    pct_jump = np.random.normal(params["jdm"]["mu_jump"], params["jdm"]["sigma_jump"])
    value *= 1 + direction * pct_jump

    pre_values = gbm_values[:jump_point+1].tolist()
    remaining_shocks = shocks[jump_point:]
    post_values = value * np.exp(np.cumsum(remaining_shocks))
    total_values = pre_values + post_values.tolist()

    return total_values, direction * pct_jump, jump_point


def get_market_stats(prices):
    prices = np.array(prices)
    log_rets = np.log(prices[1:] / prices[:-1])
    mu = np.mean(log_rets)
    sigma_est = np.std(log_rets)
    return mu, sigma_est


file_path = os.path.join(base_dir, params["jdm"]["data_set"])
df = pd.read_csv(file_path, parse_dates=["Open time"], index_col="Open time")
close_prices = np.array(df["Close"].tail(periods))

init_value = float(close_prices[0])
real_prices = close_prices

simulated_prices = calc_gbm_values(
    init_value=init_value,
    periods=periods,
    drift=drift,
    volatility=sigma
)

simulated_prices = np.array(simulated_prices)

plt.figure(figsize=(12, 6)) # ny figur, 12x6 tommer
plt.plot(real_prices, label="Real BTC", alpha=0.7) #plot BTC
plt.plot(simulated_prices, label="Simulated GBM", alpha=0.7) #plot GBM
plt.xlabel("Time Period")
plt.ylabel("Price")
plt.title("GBM Validation: Real vs Simulated (no jump)")
plt.legend() #vis labels
plt.show() #vis plottet 