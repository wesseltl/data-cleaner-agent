# Agentic Data Cleaner

An **agentic workflow** that cleans messy CSVs: a *planner* reasons about the data and decides which
cleaning steps are needed, and a set of deterministic *tools* carry them out.

## The idea, and the one design decision that matters

An "agentic workflow" sounds mysterious; it's just software with a few parts:

```
   profile the data  →  planner picks tools  →  run the tools  →  report
                        (the reasoning step)     (trusted code)
```

The decision that makes this *trustworthy*:

> **The model plans; deterministic code executes.**
> The planner decides *which* tool to run on *which* column, but the tools do the actual
> transformation. So the model never invents or hallucinates data values; it only chooses trusted,
> reproducible operations. Judgment from the model, execution in code.

## Two planners, one loop

| Planner | What it is | Needs |
|---|---|---|
| `RuleBasedPlanner` | Deterministic heuristics from the column profile. Runs offline. **Default.** | nothing |
| `LLMPlanner` | Sends the profile + tool catalog to an LLM, parses back a JSON plan. The *agentic* version. | `anthropic` + `ANTHROPIC_API_KEY` |

Both return the same action list, so the agent loop is identical, you swap the brain, not the plumbing.

## The tools (`cleaner/tools.py`)

`snake_case_headers` · `strip_whitespace` · `coerce_numeric` (€1.200,50 / $900 → floats) ·
`standardize_dates` (mixed formats → ISO) · `standardize_categorical` (NL / nederland → Netherlands) ·
`drop_duplicate_rows`

Take **`standardize_dates`**. `2023-01-05` (year-first, month in the middle) and
`05/01/2023` (day-first) need *opposite* parsing rules, a single global setting corrupts one or the
other, so the tool decides per value. Mixed dates are genuinely ambiguous, and this handles them explicitly.

## Run it

```bash
python3 __main__.py examples/messy.csv cleaned.csv    # clean a CSV (offline, rule-based)
python3 -m unittest discover -s tests                 # run the tests
```

To make it LLM-driven, pass `LLMPlanner()` to `clean()` (needs `pip install anthropic` + an API key).

## What it demonstrates

The core shape of an agentic workflow, profile → plan → act → report, with a safe, honest design
(the LLM reasons, trusted code executes), a swappable planner, thoughtful handling of a genuinely
messy problem, and a unit-tested core.
