"""CLI — clean a messy CSV.

    python3 -m data_cleaner_agent <input.csv> [output.csv]

Uses the offline rule-based planner by default. To use the LLM planner, edit run() to pass
LLMPlanner() (needs the `anthropic` package + ANTHROPIC_API_KEY).
"""
from __future__ import annotations

import sys

import pandas as pd

from cleaner.agent import clean


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 1
    src = argv[0]
    dst = argv[1] if len(argv) > 1 else None
    df = pd.read_csv(src, skipinitialspace=True)
    cleaned, log = clean(df)

    print("\nSteps taken:")
    for step in log:
        print(f"  - {step}")
    print("\nCleaned data:\n")
    print(cleaned.to_string(index=False))
    if dst:
        cleaned.to_csv(dst, index=False)
        print(f"\nWrote {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
