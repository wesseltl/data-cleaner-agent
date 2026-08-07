"""CLI — clean a messy CSV.

    python3 __main__.py <input.csv> [output.csv] [--llm]

Uses the offline rule-based planner by default. Pass --llm to use the LLM planner instead
(needs the `anthropic` package + an ANTHROPIC_API_KEY environment variable).
"""
from __future__ import annotations

import sys

import pandas as pd

from cleaner.agent import clean


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 1
    use_llm = "--llm" in argv
    args = [a for a in argv if a != "--llm"]
    src = args[0]
    dst = args[1] if len(args) > 1 else None

    planner = None
    if use_llm:
        from cleaner.planner import LLMPlanner
        planner = LLMPlanner()

    df = pd.read_csv(src, skipinitialspace=True)
    cleaned, log = clean(df, planner)

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
