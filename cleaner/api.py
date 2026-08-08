"""api.py — a small, structured interface designed to be called by other code or AI agents.

`clean_csv_text` takes CSV *text* and returns the cleaned CSV text plus a structured report of what
was done. Text in, text/JSON out — no files, no globals — which is exactly the shape an agent or an
MCP tool wants to call.
"""
from __future__ import annotations

import io

import pandas as pd

from cleaner.agent import clean


def clean_csv_text(csv_text: str, use_llm: bool = False) -> dict:
    """Clean a CSV given as text. Returns {cleaned_csv, steps, rows_in, rows_out, columns}.

    use_llm=True routes planning through the LLM planner (needs `anthropic` + ANTHROPIC_API_KEY);
    the default rule-based planner runs offline with no key.
    """
    df = pd.read_csv(io.StringIO(csv_text), skipinitialspace=True)
    rows_in = len(df)

    planner = None
    if use_llm:
        from cleaner.planner import LLMPlanner
        planner = LLMPlanner()

    cleaned, steps = clean(df, planner)
    return {
        "cleaned_csv": cleaned.to_csv(index=False),
        "steps": steps,
        "rows_in": rows_in,
        "rows_out": len(cleaned),
        "columns": list(cleaned.columns),
    }
