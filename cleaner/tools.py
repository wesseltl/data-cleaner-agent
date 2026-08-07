"""tools.py — the deterministic cleaning operations the agent can call.

Key design choice: the planner (LLM or rules) decides *which* of these to run and on which column,
but these functions do the actual transformation. That keeps cleaning reproducible and trustworthy —
the model never invents data values, it only picks trusted operations. Judgment from the model,
execution in code.

Every tool takes a DataFrame and returns a new one (no in-place surprises).
"""
from __future__ import annotations

import re

import pandas as pd


def snake_case_headers(df: pd.DataFrame) -> pd.DataFrame:
    def snake(name: str) -> str:
        name = re.sub(r"[\s\-]+", "_", str(name).strip())
        name = re.sub(r"[^\w]", "", name)
        return name.lower()
    return df.rename(columns={c: snake(c) for c in df.columns})


def strip_whitespace(df: pd.DataFrame, column: str) -> pd.DataFrame:
    df = df.copy()
    df[column] = df[column].map(lambda v: v.strip() if isinstance(v, str) else v)
    return df


def coerce_numeric(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Turn messy money/number strings ('€1.200,50', '$900', '1 000') into floats."""
    df = df.copy()

    def parse(v):
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return v
        if isinstance(v, str):
            t = re.sub(r"[^\d,.\-]", "", v)            # drop currency symbols, spaces, letters
            if "," in t and "." in t:                  # 1.200,50 -> 1200.50  (EU thousands+decimal)
                t = t.replace(".", "").replace(",", ".")
            elif "," in t:                             # 900,50 -> 900.50
                t = t.replace(",", ".")
            try:
                return float(t)
            except ValueError:
                return None
        try:
            return float(v)                            # already a number (e.g. 1000) -> float
        except (TypeError, ValueError):
            return v
    df[column] = df[column].map(parse)
    return df


def standardize_dates(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Parse mixed date formats to ISO (YYYY-MM-DD); unparseable -> None.

    Year-first values (2023-01-05, 2023/03/01) have the month in the middle, so they must NOT be read
    day-first; day/month-first values (05/01/2023) must. One global `dayfirst` can't do both, so we
    decide per value: if it starts with a 4-digit year, read it year-first, else day-first.
    """
    df = df.copy()

    def parse_one(v):
        if not isinstance(v, str):
            return None
        s = v.strip()
        year_first = bool(re.match(r"^\d{4}[-/]", s))          # 2023-.. / 2023/..
        dt = pd.to_datetime(s, errors="coerce", dayfirst=not year_first)
        return dt.strftime("%Y-%m-%d") if pd.notna(dt) else None
    df[column] = df[column].map(parse_one)
    return df


def standardize_categorical(df: pd.DataFrame, column: str, mapping: dict) -> pd.DataFrame:
    """Map value variants to a canonical form (case-insensitive), e.g. NL/nederland -> Netherlands."""
    df = df.copy()
    m = {str(k).strip().lower(): v for k, v in mapping.items()}
    df[column] = df[column].map(
        lambda v: m.get(v.strip().lower(), v) if isinstance(v, str) else v)
    return df


def drop_duplicate_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().reset_index(drop=True)
