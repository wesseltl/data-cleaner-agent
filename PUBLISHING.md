# Publishing & agent discoverability

How to make this tool findable: installable by name on PyPI, and listed where AI agents (and people)
discover MCP servers. Each step you run once.

---

## 1. Publish to PyPI (so `pip install data-cleaner-agent` works by name)

The package already builds and passes validation (`python -m build`, `twine check dist/*`).

**One-time setup:**
1. Make a free account at https://pypi.org/account/register/
2. Create an API token: PyPI → Account settings → API tokens → *Add API token* (scope: entire account for the first upload).

**Publish:**
```bash
pip install build twine
python -m build                     # creates dist/*.whl and dist/*.tar.gz
twine upload dist/*                 # username: __token__   password: your pypi token
```

Tip: test it first on TestPyPI (`twine upload --repository testpypi dist/*`) if you want a dry run.

After this, anyone (or any agent) can run:
```bash
pip install data-cleaner-agent
```

To release a new version later: bump `version` in `pyproject.toml`, rebuild, upload again.

---

## 2. List the MCP server so agents can discover it

Once it's on PyPI, submit it to the places agents and developers look for MCP tools.

**a. `awesome-mcp-servers`** (the main community directory)
- Repo: https://github.com/punkpeye/awesome-mcp-servers
- Fork it, add one line under the relevant category, open a pull request:
  ```
  - [data-cleaner-agent](https://github.com/wesseltl/data-cleaner-agent) - Clean messy CSVs from an agent: an LLM picks the steps, tested code does the work (values are never touched by the model).
  ```

**b. The official MCP registry**
- https://github.com/modelcontextprotocol/registry - follow its submission instructions to add the server.

**c. MCP directories** such as https://mcp.so and https://glama.ai/mcp/servers - submit the GitHub URL.

---

## 3. Human discovery (the launch post)

Registries make it findable to agents; a launch post makes it findable to people (which is where the
first users, stars, and reputation come from). Post the write-up (in `LAUNCH.md`) to r/Python,
r/dataengineering, Hacker News (Show HN), and LinkedIn.
