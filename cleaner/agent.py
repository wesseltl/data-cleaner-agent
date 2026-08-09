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


def _what_happened(tool: str, column: str, before: pd.Series, after: pd.Series, params: dict) -> str:
    """Describe what an operation actually did, and flag where it couldn't get a clean result.

    The point (per the r/mcp thread): let the caller tell a clean parse from a confident guess. So we
    surface the values a conversion couldn't handle, rather than silently producing tidy output.
    """
    if tool in ("coerce_numeric", "standardize_dates"):
        # values that had content but came out empty = the operation couldn't parse them
        failed = int((before.notna() & after.isna()).sum())
        total = int(before.notna().sum())
        if failed:
            return f"{tool}({column}): {failed}/{total} value(s) could not be parsed, set to null"
        return f"{tool}({column}): all {total} value(s) parsed cleanly"
    if tool == "standardize_categorical":
        mapping = {str(k).strip().lower() for k in params.get("mapping", {})}
        vals = before.dropna()
        unmapped = sorted({str(v) for v in vals if isinstance(v, str) and v.strip().lower() not in mapping})
        if unmapped:
            shown = unmapped[:5]
            more = f" (+{len(unmapped) - 5} more)" if len(unmapped) > 5 else ""
            return f"{tool}({column}): {len(unmapped)} value(s) not in the mapping, left unchanged: {shown}{more}"
        return f"{tool}({column}): every value matched the mapping"
    return f"{tool}({column})"


def clean(df: pd.DataFrame, planner=None) -> tuple[pd.DataFrame, list[str]]:
    """Clean a DataFrame. Returns (clean_df, log).

    The log reports what each step actually did, including where a conversion couldn't produce a clean
    result (unparseable numbers/dates, unmapped categories), so a clean parse is distinguishable from a
    confident guess.
    """
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
        col = a["column"]
        before = df[col].copy() if col in df.columns else None
        df = fn(df, col, **a.get("params", {}))
        if before is not None and col in df.columns:
            log.append(_what_happened(a["tool"], col, before, df[col], a.get("params", {})))
        else:
            log.append(f"{a['tool']}({col})")

    before_rows = len(df)
    df = tools.drop_duplicate_rows(df)                   # always de-dupe at the end
    log.append(f"drop_duplicate_rows (removed {before_rows - len(df)})")
    return df, log
