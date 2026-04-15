# Phase 1: Capture Layer - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

zsh plugin that captures command context (command text, stderr, exit code) via preexec/precmd hooks and provides a `??` widget to trigger explanation. The widget calls a stub Python CLI in this phase; real CLI implementation comes in Phase 2.

</domain>

<decisions>
## Implementation Decisions

### Stderr Capture
- **D-01:** Use temp file redirect for stderr capture (most reliable, handles background jobs and edge cases)
- **D-02:** Tee stderr to both terminal and file (errors visible in real-time, also captured for `??` later)
- **D-03:** Stderr written to `/tmp/shell-explainer-last-stderr`

### Widget Scope
- **D-04:** `??` widget defined in Phase 1
- **D-05:** Widget calls stub Python CLI that prints placeholder message (e.g., "CLI not implemented yet")
- **D-06:** Real CLI implementation deferred to Phase 2

### Claude's Discretion
- Hook registration pattern (preexec_functions vs direct function) — planner can choose standard zsh plugin pattern
- Plugin file structure (single file vs multiple) — planner can choose based on complexity
- Exact mechanism for stderr redirect in preexec — planner to implement based on D-01, D-02

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project vision, constraints, key decisions
- `.planning/REQUIREMENTS.md` — CAPT-01 through CAPT-05 requirements
- `.planning/research/STACK.md` — zsh hook patterns, preexec/precmd documentation

### Research Findings
- `.planning/research/PITFALLS.md` — Hook race conditions, `_functions` array pattern
- `.planning/research/ARCHITECTURE.md` — Data flow from hooks to tmp files to widget

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
None — greenfield project.

### Established Patterns
None — greenfield project.

### Integration Points
- Widget invokes Python CLI at `explainer.py` (stub in this phase)
- Temp files in `/tmp/`: `shell-explainer-last-cmd`, `shell-explainer-last-stderr`, `shell-explainer-last-exit`

</code_context>

<specifics>
## Specific Ideas

- Follow standard zsh plugin pattern (like zsh-autosuggestions, zoxide)
- Use `preexec_functions+=()` to avoid conflicts with other plugins (per PITFALLS.md)
- Clear tmp files on shell startup to avoid stale data

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-capture-layer*
*Context gathered: 2026-04-15*
