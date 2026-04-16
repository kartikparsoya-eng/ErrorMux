# Phase 2: CLI + Ollama Core - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Python CLI that reads captured command context (cmd, stderr, exit code) from temp files, calls Ollama localhost:11434 with gemma3:4b, and streams formatted WHY/FIX output via Rich. Includes graceful degradation on timeout/failure.

</domain>

<decisions>
## Implementation Decisions

### Prompt Structure
- **D-01:** Use system + user message format with ollama.chat()
- **D-02:** Ask for labeled sections: `WHY: <sentence>\nFIX: <command>` format
- **D-03:** System prompt is shell-aware (mentions zsh, common patterns) for better context

### Output Formatting
- **D-04:** Use streaming (stream=True) from Ollama for perceived speed
- **D-05:** Buffer streamed response, parse WHY/FIX after stream ends, then print with Rich formatting
- **D-06:** Compact layout: two lines max — `WHY: <dim gray text>` then `FIX: <bold green command>`
- **D-07:** WHY printed in dim gray, FIX printed in bold green

### Error Handling
- **D-08:** Ollama service down → print `[explainer offline]` and exit 0 (graceful, non-intrusive)
- **D-09:** Single 10s timeout on ollama.Client() — no retry, no progress indication
- **D-10:** Unparseable response → print raw output (user still gets value)

### Claude's Discretion
- Exact wording of system prompt — planner to craft based on D-01, D-02, D-03
- Regex pattern for WHY/FIX parsing — planner to implement based on D-02
- Whether to use Rich Console or plain print with Rich markup — planner to choose

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project vision, constraints (gemma3:4b, 10s timeout, localhost:11434)
- `.planning/REQUIREMENTS.md` — CLI-01, CLI-04, CLI-05, CLI-06 requirements
- `.planning/research/STACK.md` — ollama SDK usage patterns, timeout handling, streaming patterns

### Prior Phase Context
- `.planning/phases/01-capture-layer/01-CONTEXT.md` — Temp file locations, widget behavior

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/errormux/cli.py` — Stub CLI with `explain()` command (21 lines) — extend this
- `pyproject.toml` — Already has typer, rich dependencies

### Established Patterns
- CLI entry point: `errormux` command (already registered in pyproject.toml)
- Widget calls `errormux` (from Phase 1, line 82 of errormux.plugin.zsh)

### Integration Points
- Temp files to read:
  - `/tmp/shell-explainer-last-cmd` — command text
  - `/tmp/shell-explainer-last-stderr` — stderr output
  - `/tmp/shell-explainer-last-exit` — exit code
- Need to add: `ollama` to dependencies (use `uv add ollama`)

</code_context>

<specifics>
## Specific Ideas

- Follow ollama SDK pattern from STACK.md: `Client(host='http://localhost:11434', timeout=10.0)`
- Use `client.chat(model='gemma3:4b', messages=[...], stream=True)`
- Handle `httpx.TimeoutException` and `ollama.ResponseError` for graceful degradation

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-cli-ollama-core*
*Context gathered: 2026-04-15*
