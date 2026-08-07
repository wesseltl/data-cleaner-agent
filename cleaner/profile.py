"""profile.py — inspect a table so the planner can decide what needs cleaning.

The profile is what the 'brain' (rule-based or LLM) looks at: per column, its type, how much is
missing, how many distinct values, and a few samples. Cheap to compute, and it's all the planner
needs to reason about the data.
"""
from __future__ import annotations

import pandas as pd


def profile_frame(df: pd.DataFrame, sample: int = 4) -> list[dict]:
    out = []
    for col in df.columns:
        s = df[col]
        out.append({
            "column": str(col),
            "dtype": str(s.dtype),
            "n_missing": int(s.isna().sum()),
            "n_unique": int(s.nunique(dropna=True)),
            "samples": [str(v) for v in s.dropna().unique()[:sample]],
        })
    return out
