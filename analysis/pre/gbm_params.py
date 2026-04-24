import numpy as np
import json
import yaml
import os
import pandas as pd

def load_and_window(data_set_path, freq_seconds=60):
    """
    Load the price CSV, resample to `freq_seconds` intervals, and split
    the price series into complete 1-day windows.
    Returns an (n_windows, bars_per_day) array of prices.
    """
    if freq_seconds < 60:
        raise ValueError(f"freq_seconds must be >=60, got {freq_seconds}.")

    df = pd.read_csv(data_set_path, parse_dates=["Open time"], index_col="Open time")
    print(f"Loaded {len(df):,} rows, {df.index.min()} → {df.index.max()}")

    series = df["Close"]
    if freq_seconds > 60:
        series = series.resample(f"{freq_seconds}s").last().dropna()

    expected_per_day = 86400 // freq_seconds
    windows = [g.values for _, g in series.groupby(series.index.floor("D"))
               if len(g) == expected_per_day]

    if not windows:
        raise ValueError(
            f"No complete 1-day windows found at freq_seconds={freq_seconds} "
            f"(expected {expected_per_day} bars/day)."
        )

    print(f"Built {len(windows):,} complete 1-day windows of {expected_per_day} bars each.")
    return np.asarray(windows)


def est_gbm_params(price_windows, max_bar_threshold=0.015):
    """
    Compute log returns within each 1-day price window, then estimate
    (mu, sigma) per window. Excludes windows containing any single-bar
    log return exceeding `max_bar_threshold` (flash-crash filter), then
    trims to the 1st-99th sigma percentile. Returns paired distributions
    so joint sampling preserves correlation.
    """
    price_windows = np.asarray(price_windows)
    log_returns = np.log(price_windows[:, 1:] / price_windows[:, :-1])
    n_windows = len(log_returns)

    window_max_abs = np.abs(log_returns).max(axis=1)
    keep = window_max_abs <= max_bar_threshold

    print(f"Flash-crash filter: kept {keep.sum():,} of {n_windows:,} windows "
          f"({100 * keep.mean():.1f}%) at threshold {max_bar_threshold}")

    log_returns = log_returns[keep]

    window_mus = log_returns.mean(axis=1)
    window_sigmas = log_returns.std(axis=1, ddof=1)

    lo, hi = np.percentile(window_sigmas, [1, 99])
    mask = (window_sigmas >= lo) & (window_sigmas <= hi)
    window_mus = window_mus[mask]
    window_sigmas = window_sigmas[mask]

    return window_mus.tolist(), window_sigmas.tolist()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(base_dir, "../../config/params.yaml")
    dist_path = os.path.join(base_dir, "../../config/jdm_distributions.json")

    with open(yaml_path,"r") as f:
        params = yaml.safe_load(f)

    data_set = params["jdm"]["data_set"]

    print(f"Loading {data_set} ...")
    price_windows = load_and_window(
        os.path.join(base_dir, "../..", data_set),
        freq_seconds=params["jdm"]["bar_seconds"],
    )

    window_mus, window_sigmas = est_gbm_params(price_windows)

    print(f"\nEstimated from {len(window_mus):,} windows.")
    print(
        f"  sigma: mean={np.mean(window_sigmas):.4f}, "
        f"range=[{min(window_sigmas):.4f}, {max(window_sigmas):.4f}]"
    )

    with open(dist_path, "w") as f:
        json.dump({"mu": window_mus, "sigma": window_sigmas}, f, indent=1)

    params["jdm"]["distributions_file"] = "config/jdm_distributions.json"

    with open(yaml_path, "w") as f:
        yaml.dump(params, f)

    print(f"\nDistributions → {dist_path}")
    print(f"Config updated → {yaml_path}")