"""mcp_server.py — expose the CSV cleaner as an MCP tool that other AI agents can call.

MCP (Model Context Protocol) is the standard way to give an AI agent tools. Running this as an MCP
server lets an agent (Claude Desktop, or any MCP client) clean a messy CSV by calling a tool, instead
of trying to reformat the data itself in the prompt (which is slow and can corrupt values).

Run:  python -m cleaner.mcp_server        (needs:  pip install "data-cleaner-agent[mcp]")

Then point your MCP client at this command. The agent gets one tool, `clean_csv`, that takes CSV text
and returns the cleaned CSV plus the list of steps taken.
"""
from __future__ import annotations

from cleaner.api import clean_csv_text

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "The MCP server needs the 'mcp' package. Install it with:\n"
        '    pip install "data-cleaner-agent[mcp]"'
    ) from exc

mcp = FastMCP("data-cleaner")


@mcp.tool()
def clean_csv(csv_text: str) -> dict:
    """Clean a messy CSV given as text.

    Fixes headers (snake_case), trims whitespace, parses mixed date formats to ISO, turns money
    strings (e.g. "€1.200,50") into numbers, standardizes known categories, and drops duplicate rows.
    Returns the cleaned CSV text and the list of steps that were applied.

    The cleaning transformations are done by deterministic, tested code — the values are never
    invented or rewritten by a language model.

    Args:
        csv_text: the raw CSV content, including the header row.
    """
    return clean_csv_text(csv_text)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
