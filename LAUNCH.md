# Launch post

Ready-to-post write-up for r/Python, r/dataengineering, Hacker News (Show HN), and LinkedIn.

---

**Title:** Show HN: A CSV cleaner where the LLM picks the steps but never touches your data

**Body:**

I kept seeing "clean this CSV with an LLM" tools that pipe your data through a model and hope it
doesn't quietly change values. That felt backwards. Language models are good at judgment ("this column
looks like money") and bad at being a reliable calculator.

So I built it the other way around. An LLM (or a set of offline rules) only decides *which* cleaning
step runs on *which* column. The actual transformations are plain tested Python functions. The model
plans the cleanup; it never reads a value and writes back a "cleaned" one. Nothing gets hallucinated.

It handles the usual mess in one pass: inconsistent headers, whitespace, mixed date formats
(2023-01-05 vs 05/01/2023, which need opposite parsing rules), money strings like €1.200,50, category
variants, and duplicate rows.

Runs offline with no API key by default. You can also drive the planning with an LLM, and other AI
agents can call it as an MCP tool instead of reformatting CSVs token by token.

    pip install git+https://github.com/wesseltl/data-cleaner-agent

Code: https://github.com/wesseltl/data-cleaner-agent

Feedback welcome, especially on the date-parsing edge cases.

---

**Shorter LinkedIn version:**

I built a small tool that cleans messy CSVs with an honest twist: the LLM decides *which* cleaning
steps the data needs, but tested Python code does the actual work. The model never touches your data
values, so nothing gets hallucinated or silently rewritten.

It fixes headers, whitespace, mixed date formats, money strings (€1.200,50 → 1200.50), category
variants, and duplicates in one pass. Runs offline, and other AI agents can call it as an MCP tool.

Code + demo: https://github.com/wesseltl/data-cleaner-agent
