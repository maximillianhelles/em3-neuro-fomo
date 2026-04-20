import numpy as np
import json
import yaml
import os
import pandas as pd

def est_gbm_params_window(series, window_size=288, freq_seconds=60, max_bar_threshold=0.015):
    """
    Estimate (mu, sigma) for each non-overlapping window of the series.
    Excludes windows containing any single-bar log return exceeding
    `max_bar_threshold` (flash-crash filter).
    Returns paired distributions so joint sampling preserves correlation.
    """
    if freq_seconds < 60:
        raise ValueError(f"freq_seconds must be ≥60, got {freq_seconds}.")
    if freq_seconds > 60:
        series = series.resample(f"{freq_seconds}s").last().dropna()

    log_rets = np.log(series / series.shift(1)).dropna()

    n_windows = len(log_rets) // window_size
    if n_windows < 1:
        raise ValueError(
            f"Series too short: {len(log_rets)} returns, need ≥{window_size}."
        )

    trimmed = log_rets.iloc[:n_windows * window_size]
    windows = trimmed.values.reshape(n_windows, window_size)

    # Flash-crash filter: exclude windows with any bar exceeding threshold
    window_max_abs = np.abs(windows).max(axis=1)
    keep = window_max_abs <= max_bar_threshold

    print(f"Flash-crash filter: kept {keep.sum():,} of {n_windows:,} windows "
          f"({100 * keep.mean():.1f}%) at threshold {max_bar_threshold}")

    windows = windows[keep]

    # Exlcude any extremes by keeping 1st-99th percentile of sigmas 
    window_mus = windows.mean(axis=1)
    window_sigmas = windows.std(axis=1, ddof=1)

    lo, hi = np.percentile(window_sigmas, [1, 99])
    mask = (window_sigmas >= lo) & (window_sigmas <= hi)
    window_mus = window_mus[mask]
    window_sigmas = window_sigmas[mask]

    return window_mus.tolist(), window_sigmas.tolist()

base_dir = os.path.dirname(os.path.abspath(__file__))
yaml_path = os.path.join(base_dir, "../../config/params.yaml")
dist_path = os.path.join(base_dir, "../../config/jdm_distributions.json")

with open(yaml_path,"r") as f:
    params = yaml.safe_load(f)

data_set = params["jdm"]["data_set"]

print(f"Loading {data_set} ...")
df = pd.read_csv(
    os.path.join(base_dir, "../..", data_set),
    parse_dates=["Open time"],
    index_col="Open time"
)
print(f"Loaded {len(df):,} rows, {df.index.min()} → {df.index.max()}")

window_mus, window_sigmas = est_gbm_params_window(
    df["Close"],
    window_size=params["jdm"]["periods"],
    freq_seconds=params["jdm"]["bar_seconds"],
)

print(f"\nEstimated from {len(window_mus):,} windows.")
print(
    f"  sigma: mean={np.mean(window_sigmas):.4f}, "
    f"range=[{min(window_sigmas):.4f}, {max(window_sigmas):.4f}]"
)

dist_path = os.path.join(base_dir, "../../config/jdm_distributions.json")
with open(dist_path, "w") as f:
    json.dump({"mu": window_mus, "sigma": window_sigmas}, f, indent=1)

params["jdm"]["distributions_file"] = "config/jdm_distributions.json"

with open(yaml_path, "w") as f:
    yaml.dump(params, f)

print(f"\nDistributions → {dist_path}")
print(f"Config updated → {yaml_path}")