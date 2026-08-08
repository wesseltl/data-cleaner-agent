# data-cleaner-agent

Clean a messy CSV with an agentic workflow. An LLM decides *which* cleaning steps the data needs, and
tested Python functions do the actual work. **The model plans the cleanup, it never touches your data
values**, so nothing gets hallucinated or silently rewritten.

Works offline out of the box (no API key). Can be driven by an LLM, and other AI agents can call it as
an [MCP](https://modelcontextprotocol.io) tool.

## Before / after

```
Full Name , Country, Signup Date, Amount Paid          full_name    country  signup_date  amount_paid
 Alice  ,Netherlands,2023-01-05,"€1.200,50"                Alice  Netherlands   2023-01-05       1200.5
Bob,nederland,05/01/2023,"$900"              ─────▶          Bob  Netherlands   2023-01-05        900.0
 Alice  ,NL,2023-01-05,"€1.200,50"                         Carol      Germany   2023-02-10       1000.0
Carol , Germany ,2023-02-10,1000                             Dan      Belgium   2023-03-01        750.0
Dan,belgie,2023/03/01,"€ 750,00"
```

In one pass it fixed the headers, trimmed whitespace, parsed three different date formats to ISO,
turned `€1.200,50` / `$900` / `€ 750,00` into numbers, standardized the country names, and dropped the
duplicate Alice row.

## Install & run

```bash
pip install git+https://github.com/wesseltl/data-cleaner-agent

clean-csv messy.csv cleaned.csv       # clean a file
clean-csv messy.csv                   # or just print the result
```

No API key needed. The default planner is a set of offline heuristics.

## The idea

An "agentic workflow" is just software with a few parts:

```
   look at the data   ->   planner picks the steps   ->   run the steps   ->   report
                           (rules, or an LLM)             (tested code)
```

The decision that makes it safe to trust:

> **The planner decides *which* tool runs on *which* column. The tools do the transformation.**
> A language model is good at judgment ("this column looks like money") and bad at being a reliable
> calculator. So the LLM only ever *picks* operations from a fixed set. It never reads a value and
> writes back a "cleaned" one, which is where LLM data-cleaning usually goes wrong.

## Two planners, one loop

| Planner | What it is | Needs |
|---|---|---|
| `RuleBasedPlanner` | Offline heuristics from a quick data profile. The default. | nothing |
| `LLMPlanner` | Sends the profile + tool list to an LLM, gets back a JSON plan. | `pip install "data-cleaner-agent[llm]"` + `ANTHROPIC_API_KEY` |

Both return the same list of steps, so the loop is identical. You swap the brain, not the plumbing.

## Use it from other code or agents

```python
from cleaner.api import clean_csv_text

result = clean_csv_text(open("messy.csv").read())
print(result["cleaned_csv"])
print(result["steps"])
```

### As an MCP tool

Other AI agents (Claude Desktop, or any MCP client) can call the cleaner as a tool, so they can clean
a CSV properly instead of reformatting it token by token in the prompt:

```bash
pip install "data-cleaner-agent[mcp]"
python -m cleaner.mcp_server
```

This exposes one tool, `clean_csv`, that takes CSV text and returns the cleaned CSV plus the steps.

## What's in the box

`cleaner/tools.py` holds the transformations: `snake_case_headers`, `strip_whitespace`,
`coerce_numeric`, `standardize_dates`, `standardize_categorical`, `drop_duplicate_rows`.

Take `standardize_dates`. `2023-01-05` (year first, month in the middle) and `05/01/2023` (day first)
need opposite parsing rules, and one global setting corrupts one or the other, so the tool decides per
value. Mixed dates are genuinely ambiguous, and this handles them explicitly instead of guessing.

## Tests

```bash
python -m unittest discover -s tests
```

## License

MIT.
