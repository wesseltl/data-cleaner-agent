"""agent.py — the workflow loop that ties the pieces together.

    profile the data  ->  planner chooses tools  ->  run the tools  ->  report what happened

This is the whole "agentic workflow" in one function: a planner (the reasoning step) picks actions
from a tool catalog, and the loop executes them with trusted code. Swap RuleBasedPlanner for LLMPlanner
and the exact same loop becomes LLM-driven.
"""
from __future__ import annotations

import pandas as pd

from cleaner import tools
from cleaner.planner import RuleBasedPlanner
from cleaner.profile import profile_frame

# the tools the agent is allowed to dispatch (a whitelist — the planner can't run arbitrary code)
DISPATCH = {
    "strip_whitespace": tools.strip_whitespace,
    "coerce_numeric": tools.coerce_numeric,
    "standardize_dates": tools.standardize_dates,
    "standardize_categorical": tools.standardize_categorical,
}


def clean(df: pd.DataFrame, planner=None) -> tuple[pd.DataFrame, list[str]]:
    """Clean a DataFrame. Returns (clean_df, log-of-steps-taken)."""
    planner = planner or RuleBasedPlanner()
    log: list[str] = [f"planner: {planner.name}"]

    df = tools.snake_case_headers(df)                     # always normalise headers first
    log.append("snake_case_headers")

    actions = planner.plan(profile_frame(df))            # the reasoning step
    for a in actions:
        fn = DISPATCH.get(a["tool"])
        if fn is None:
            log.append(f"skipped unknown tool: {a['tool']}")
            continue
        df = fn(df, a["column"], **a.get("params", {}))
        log.append(f"{a['tool']}({a['column']})")

    before = len(df)
    df = tools.drop_duplicate_rows(df)                   # always de-dupe at the end
    log.append(f"drop_duplicate_rows (removed {before - len(df)})")
    return df, log
