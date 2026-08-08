# Security

This tool is designed to be safe to point at real data. Here is exactly what it does and does not do,
including one important distinction between its two modes.

## Default mode (rule-based planner): fully local

Out of the box, cleaning is planned by offline heuristics. In this mode:

- **Runs locally.** Executes as a normal Python process on your machine.
- **No network calls.** Nothing is sent anywhere. Your data stays on the machine.
- **No telemetry.** No usage data is collected.
- **Deterministic transforms.** Values are transformed by plain tested Python (`pandas`). The cleaning
  is reproducible; nothing is invented.
- **Open source (MIT).** Fully auditable in this repository.

## Optional LLM mode (`--llm` / `LLMPlanner`): sends a data *profile* to an API

If you explicitly enable the LLM planner, the tool sends a **column profile** to an LLM provider
(Anthropic) to decide which cleaning steps to run. Be aware:

- The profile includes column names, data types, and a **few sample values per column** (not the full
  dataset, but not nothing either).
- This means some of your data leaves your machine and is processed by a third-party API under their
  terms.
- **Do not enable LLM mode on sensitive or regulated data** unless that data-sharing is acceptable to
  you. The default (rule-based) mode does not do this.

Even in LLM mode, the model only *chooses which tools to run*. The actual cell transformations are
still done by local deterministic code; the model never rewrites your values directly.

## Reporting an issue

Found a security problem? Please open an issue, or email wesseltl@gmail.com.
