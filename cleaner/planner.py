"""planner.py — decides WHICH cleaning tools to run. The 'brain' of the agentic workflow.

Two implementations behind one interface:

  * RuleBasedPlanner — deterministic heuristics. Runs offline, no API key. The default, so the whole
    workflow runs and is testable without a model.
  * LLMPlanner — sends the data profile + the tool catalog to an LLM and parses back a JSON plan.
    This is the *agentic* version: the model reasons about the data and chooses the steps. You plug
    in your API key; it's a drop-in for the rule-based one because it returns the same action list.

An "action" is a small dict: {"tool": <name>, "column": <name or None>, "params": {...}}.
"""
from __future__ import annotations

import json
import re

# a tiny example lookup; a real project would load a fuller list
COUNTRY_MAP = {
    "nl": "Netherlands", "nederland": "Netherlands", "netherlands": "Netherlands", "holland": "Netherlands",
    "de": "Germany", "germany": "Germany", "duitsland": "Germany",
    "be": "Belgium", "belgium": "Belgium", "belgie": "Belgium", "belgië": "Belgium",
}

_DATE_RE = re.compile(r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}")
_MONEYISH_RE = re.compile(r"[€$£]|\d[.,]\d")


def _fraction(samples, pred) -> float:
    return sum(1 for s in samples if pred(s)) / len(samples) if samples else 0.0


class RuleBasedPlanner:
    """Heuristic planner — good enough to run the whole workflow with zero dependencies."""
    name = "rule-based"

    def plan(self, profile: list[dict]) -> list[dict]:
        actions: list[dict] = []
        for col in profile:
            name, samples = col["column"], col["samples"]
            if any(isinstance(s, str) and s != s.strip() for s in samples):
                actions.append({"tool": "strip_whitespace", "column": name})
            if "country" in name or name in ("land", "nationality"):
                actions.append({"tool": "standardize_categorical", "column": name,
                                "params": {"mapping": COUNTRY_MAP}})
            elif _fraction(samples, lambda s: bool(_MONEYISH_RE.search(s))) >= 0.5:
                actions.append({"tool": "coerce_numeric", "column": name})
            elif "date" in name or _fraction(samples, lambda s: bool(_DATE_RE.search(s))) >= 0.5:
                actions.append({"tool": "standardize_dates", "column": name})
        return actions


TOOL_CATALOG = """
Available tools (choose which to run per column):
- strip_whitespace(column)        : trim leading/trailing spaces from string values
- coerce_numeric(column)          : turn money/number strings into floats
- standardize_dates(column)       : parse mixed date formats to YYYY-MM-DD
- standardize_categorical(column, mapping) : map value variants to a canonical form
""".strip()


class LLMPlanner:
    """The agentic version: an LLM reads the profile and returns a JSON cleaning plan.

    Requires the `anthropic` package and an ANTHROPIC_API_KEY. Kept dependency-free at import time so
    the rest of the project runs without it — you only need it when you actually use this planner.
    """
    name = "llm"

    def __init__(self, model: str = "claude-sonnet-5", api_key: str | None = None):
        self.model = model
        self.api_key = api_key

    def plan(self, profile: list[dict]) -> list[dict]:
        import os

        import anthropic  # imported lazily so it's optional
        client = anthropic.Anthropic(api_key=self.api_key or os.environ["ANTHROPIC_API_KEY"])
        prompt = (
            "You are a data-cleaning planner. Given a column profile, decide which tools to run.\n\n"
            f"{TOOL_CATALOG}\n\n"
            f"Column profile:\n{json.dumps(profile, indent=2)}\n\n"
            'Reply with ONLY a JSON array of actions, each like '
            '{"tool": "...", "column": "...", "params": {}}. No prose.'
        )
        msg = client.messages.create(
            model=self.model, max_tokens=1024,
            messages=[{"role": "user", "content": prompt}])
        text = msg.content[0].text.strip()
        text = re.sub(r"^```(json)?|```$", "", text, flags=re.MULTILINE).strip()
        return json.loads(text)     # the model's plan, ready for the same agent loop
