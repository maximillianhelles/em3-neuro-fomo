"""
load_trials.py

Loads behavioral trial data into a flat pandas DataFrame with the 25-column
schema agreed in planning. One row per trial. Excludes data/behavioral_data/
excluded/.

Usage:
    from load_trials import load_trials, summarise_trials, dump_grouped_json

    trials = load_trials()                          # default: data/behavioral_data
    summarise_trials(trials)
    dump_grouped_json(trials, "trials.json")        # grouped-columnar export
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

# ---- Schema -----------------------------------------------------------------

COLUMN_ORDER = [
    # identifiers
    "participant_id", "block_id", "trial_num", "ticker",
    # design
    "position", "direction", "intended_condition",
    # spike & action timing
    "jump_index", "jump_pct", "action_index", "action_kind",
    "action_before_spike", "rt_samples",
    # realized condition
    "realized_position", "realized_condition", "condition_switched",
    # post-spike trajectory
    "pre_spike_value", "post_spike_value", "post_spike_extremum",
    "exit_value", "final_value", "spike_retained",
    # SAM
    "valence", "arousal", "regret",
]

# Mapping used for both the analysis schema and the JSON export grouping.
COLUMN_GROUPS = {
    "identifiers": ["participant_id", "block_id", "trial_num", "ticker"],
    "design":      ["position", "direction", "intended_condition"],
    "spike_action": [
        "jump_index", "jump_pct",
        "action_index", "action_kind", "action_before_spike", "rt_samples",
    ],
    "realized_condition": [
        "realized_position", "realized_condition", "condition_switched",
    ],
    "post_spike": [
        "pre_spike_value", "post_spike_value", "post_spike_extremum",
        "exit_value", "final_value", "spike_retained",
    ],
    "SAM": ["valence", "arousal", "regret"],
}

BLOCKS = ("control", "low", "high")  # excluded/ is intentionally absent


# ---- Parsers ---------------------------------------------------------------

def _parse_chart_values(s: str) -> list[float]:
    return ast.literal_eval(s)


def _parse_action_kind(s: str) -> str | None:
    # "(True, 'BUY')" -> "BUY"; "(False, None)" -> None
    if "BUY" in s:
        return "BUY"
    if "SELL" in s:
        return "SELL"
    return None


def _label_condition(position: str, direction: int) -> str | None:
    if pd.isna(position) or pd.isna(direction):
        return None
    return {
        ("ASSET",  1): "Gain",
        ("ASSET", -1): "Loss",
        ("CASH",   1): "FOMO",
        ("CASH",  -1): "Relief",
    }.get((position, int(direction)))


# ---- Per-trial enrichment --------------------------------------------------

def _enrich_row(row: pd.Series) -> pd.Series:
    """Compute all derived columns for one trial."""
    values     = _parse_chart_values(row["chart_values"])
    jump_index = int(row["jump_index"])
    direction  = int(row["direction"])
    action_idx = row["action_index"]
    has_action = pd.notna(action_idx)
    action_idx = int(action_idx) if has_action else None
    action_val = row["action_value"] if has_action else None
    action_kind = _parse_action_kind(row["action_taken"])

    # jump_index is 0-based (Python); v[jump_index] is the FIRST post-spike sample
    # and v[jump_index - 1] is the LAST pre-spike sample.
    pre_spike_value  = values[jump_index - 1]
    post_spike_value = values[jump_index]
    post_slice = values[jump_index:]
    post_spike_extremum = max(post_slice) if direction == 1 else min(post_slice)

    # Realized condition: position held at spike onset.
    if not has_action or action_idx >= jump_index:
        realized_position = row["position"]            # no action, or after spike
    else:
        realized_position = row["final_position"]      # acted before spike

    intended_condition = _label_condition(row["position"], direction)
    realized_condition = _label_condition(realized_position, direction)

    # Exit value: SELL locks in at action; otherwise ride to end.
    exit_value = action_val if action_kind == "SELL" else row["final_value"]

    # Direction-neutral spike retention.
    denom = post_spike_value - pre_spike_value
    spike_retained = (exit_value - pre_spike_value) / denom if denom != 0 else math.nan

    return pd.Series({
        "intended_condition":   intended_condition,
        "action_kind":          action_kind,
        "action_before_spike":  (action_idx < jump_index) if has_action else None,
        "rt_samples":           (action_idx - jump_index) if has_action else None,
        "realized_position":    realized_position,
        "realized_condition":   realized_condition,
        "condition_switched":   intended_condition != realized_condition,
        "pre_spike_value":      pre_spike_value,
        "post_spike_value":     post_spike_value,
        "post_spike_extremum":  post_spike_extremum,
        "exit_value":           exit_value,
        "spike_retained":       spike_retained,
    })


# ---- Block & root loaders --------------------------------------------------

def _load_block(block_id: str, data_root: Path) -> pd.DataFrame:
    block_dir = data_root / block_id
    files = sorted(block_dir.glob("*_results_block.csv"))
    if not files:
        print(f"[warn] no files in {block_dir}")
        return pd.DataFrame()
    return pd.concat((pd.read_csv(f) for f in files), ignore_index=True)


def load_trials(data_root: str | Path = "data/behavioral_data",
                blocks: tuple[str, ...] = BLOCKS) -> pd.DataFrame:
    data_root = Path(data_root)
    raw = pd.concat(
        (_load_block(b, data_root) for b in blocks), ignore_index=True
    )
    if raw.empty:
        return raw

    # Coerce types up-front. action_index stays nullable Int64 to allow NaN.
    raw = raw.astype({
        "trial_num":   "int64",
        "direction":   "int64",
        "jump_index":  "int64",
        "jump_pct":    "float64",
        "final_value": "float64",
        "valence":     "int64",
        "arousal":     "int64",
        "regret":      "int64",
    })
    raw["action_index"] = pd.to_numeric(raw["action_index"], errors="coerce").astype("Int64")
    raw["action_value"] = pd.to_numeric(raw["action_value"], errors="coerce")

    # Apply per-row enrichment, then merge back.
    enriched = raw.apply(_enrich_row, axis=1)
    df = pd.concat([raw, enriched], axis=1)

    # Categorical with explicit ordering for downstream plotting and modelling.
    df["block_id"] = pd.Categorical(df["block_id"], categories=list(BLOCKS), ordered=True)
    for col in ("position", "realized_position"):
        df[col] = pd.Categorical(df[col], categories=["ASSET", "CASH"])
    for col in ("intended_condition", "realized_condition"):
        df[col] = pd.Categorical(df[col], categories=["Gain", "Loss", "FOMO", "Relief"])
    df["action_kind"] = pd.Categorical(df["action_kind"], categories=["BUY", "SELL"])

    return df[COLUMN_ORDER]


# ---- Diagnostics -----------------------------------------------------------

def summarise_trials(df: pd.DataFrame) -> None:
    print(f"Rows:         {len(df)}")
    print(f"Participants: {df['participant_id'].nunique()}\n")

    print("Per participant x block trial counts:")
    print(
        df.groupby(["participant_id", "block_id"], observed=True)
          .size().unstack(fill_value=0)
    )

    print("\nBy block x realized condition:")
    print(
        df.groupby(["block_id", "realized_condition"], observed=True)
          .size().unstack(fill_value=0)
    )

    print("\nSwitch rate by block:")
    print(
        df.groupby("block_id", observed=True)["condition_switched"]
          .agg(n="size", n_switched="sum", switch_rate="mean")
    )

    print("\nspike_retained distribution by realized condition:")
    print(
        df.groupby("realized_condition", observed=True)["spike_retained"]
          .agg(["min",
                lambda s: s.quantile(0.25),
                "median",
                lambda s: s.quantile(0.75),
                "max"])
          .rename(columns={"<lambda_0>": "q25", "<lambda_1>": "q75"})
    )


# ---- JSON export -----------------------------------------------------------

def _to_jsonable(value):
    """Replace NaN/NA with None and unwrap numpy scalars."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    if value is pd.NA:
        return None
    if isinstance(value, np.generic):
        return value.item()
    return value


def dump_grouped_json(df: pd.DataFrame, path: str | Path) -> None:
    """
    Write the DataFrame as grouped-columnar JSON, e.g.:
        {"identifiers": {"participant_id": [...], ...}, "design": {...}, ...}

    The flat DataFrame stays the source of truth; this is an export view.
    """
    out: dict[str, dict[str, list]] = {}
    for group, cols in COLUMN_GROUPS.items():
        out[group] = {}
        for col in cols:
            series = df[col]
            # Categoricals -> string for portability; numeric -> python scalars.
            if isinstance(series.dtype, pd.CategoricalDtype):
                series = series.astype(object)
            out[group][col] = [_to_jsonable(v) for v in series.tolist()]

    # Cheap alignment check before write: every list within and across groups
    # must have the same length.
    lengths = {
        f"{g}.{c}": len(out[g][c]) for g in out for c in out[g]
    }
    distinct = set(lengths.values())
    if len(distinct) != 1:
        raise ValueError(
            f"alignment broken before JSON dump; lengths: {lengths}"
        )

    with open(path, "w") as f:
        json.dump(out, f, indent=2)


# ---- CLI -------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--data-root", default="data/behavioral_data")
    ap.add_argument("--json-out", default=None,
                    help="If set, write grouped-columnar JSON here.")
    args = ap.parse_args()

    trials = load_trials(args.data_root)
    summarise_trials(trials)

    if args.json_out:
        dump_grouped_json(trials, args.json_out)
        print(f"\nWrote {args.json_out} ({len(trials)} trials).")