<!-- mcp-name: io.github.wesseltl/data-cleaner-agent -->

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
pip install agentic-csv-cleaner

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
| `LLMPlanner` | Sends the profile + tool list to an LLM, gets back a JSON plan. | `pip install "agentic-csv-cleaner[llm]"` + `ANTHROPIC_API_KEY` |

Both return the same list of steps, so the loop is identical. You swap the brain, not the plumbing.

The log reports what each step actually did, including where a conversion could not produce a clean
result (unparseable numbers/dates, unmapped categories), so a clean parse is distinguishable from a
confident guess.

## Use it from other code or agents

```python
from cleaner.api import clean_csv_text

result = clean_csv_text(open("messy.csv").read())
print(result["cleaned_csv"])
print(result["steps"])
```

### As an MCP tool (Claude Desktop)

Other AI agents can call the cleaner as a tool, so they clean a CSV properly instead of reformatting it
token by token in the prompt. Three steps:

**1. Install it**

```bash
pip install "agentic-csv-cleaner[mcp]"
```

**2. Add it to your client's config** (Claude Desktop's config lives at
`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS, or
`%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "csv-cleaner": { "command": "python", "args": ["-m", "cleaner.mcp_server"] }
  }
}
```

**3. Restart Claude Desktop.** The agent now has a `clean_csv` tool that takes CSV text and returns the
cleaned CSV plus a report of what it did.

### Use it with other MCP clients

The same server works in any MCP client, only the config differs. The command is
`python -m cleaner.mcp_server`.

**Cursor** — `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per project), hot-reloads:

```json
{ "mcpServers": { "csv-cleaner": { "command": "python", "args": ["-m", "cleaner.mcp_server"] } } }
```

**VS Code / GitHub Copilot** — `.vscode/mcp.json`. Note the different key (`servers`, not `mcpServers`)
and the required `type`. Tools only run in Copilot **Agent mode**:

```json
{ "servers": { "csv-cleaner": { "type": "stdio", "command": "python", "args": ["-m", "cleaner.mcp_server"] } } }
```

**Windsurf** — `~/.codeium/windsurf/mcp_config.json` (create it if missing):

```json
{ "mcpServers": { "csv-cleaner": { "command": "python", "args": ["-m", "cleaner.mcp_server"] } } }
```

**Cline** — add it from the extension's MCP settings panel in VS Code.

## Understanding the report

The tool doesn't just hand back tidy data, it tells you what each step actually did, including where it
couldn't get a clean result, so you can tell a clean parse from a confident guess:

```
- coerce_numeric(amount): all 4 value(s) parsed cleanly
- standardize_dates(signup): 1/3 value(s) could not be parsed, set to null
- standardize_categorical(country): 1 value(s) not in the mapping, left unchanged: ['MARS']
```

So instead of silently dropping a value or leaving a wrong category, it surfaces it, and you know
exactly which cells to double-check.

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
