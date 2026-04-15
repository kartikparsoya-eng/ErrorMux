# Phase 4: Skip-List Filtering - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Prevent the `??` trigger from invoking the LLM when a command's non-zero exit is semantically expected (not an error). Covers three built-in cases — grep exit 1, test/[[ exit 1, diff exit 1 — plus a user-configurable TOML list for additional patterns.

**In scope:** skip-match logic, built-in defaults, config loading, skipped-command UX.
**Out of scope:** new capture signals, LLM prompt changes, installation flow (Phase 5).
</domain>

<canonical_refs>
## Canonical References

- `.planning/ROADMAP.md` — Phase 4 goal, requirements SKIP-01..04
- `.planning/REQUIREMENTS.md` — SKIP-01..04 acceptance criteria
- `.planning/phases/02-cli-ollama-core/` — CLI entry point this phase hooks into
- `.planning/phases/03-cache-system/` — Integration pattern for CLI-side short-circuit

No external ADRs/specs referenced.
</canonical_refs>

<decisions>
## Implementation Decisions

### Match Semantics
- **D-01:** Skip rules match on `(command_name, exit_code)` pairs. `command_name` = first whitespace-separated token of the captured command line (after stripping leading env assignments if trivially doable; otherwise just the literal first token).
- **D-02:** Built-in defaults: `grep=1`, `test=1`, `[[=1`, `[=1`, `diff=1`. Exit code 2+ from these commands is NOT skipped (real errors still explained).

### Where Skipping Happens
- **D-03:** Skip check lives in the Python CLI, not the zsh hook. Hook always captures; CLI consults skip list immediately after loading cache context, before any LLM or network work.
- **D-04:** Skip check runs BEFORE cache lookup — no need to cache "skipped" states.

### Config Schema
- **D-05:** Config file: `~/.shell-explainer/config.toml` (per REQUIREMENTS).
- **D-06:** Built-ins are hardcoded in the source and always active by default. User config is additive.
- **D-07:** User can disable a built-in via a `skip.disable = ["grep"]` key (list of command names). Downstream planner picks exact TOML layout; constraint: must support add + disable.
- **D-08:** User additions support `(name, exit_code)` pairs. Exit-code ranges (e.g., `1-2`) are out of scope for this phase — single codes only.
- **D-09:** Missing or malformed config file → fall back to built-ins silently; log a warning to stderr only when `--verbose` or similar debug flag is set (planner's call on flag name).

### Skipped-Command UX
- **D-10:** When `??` fires on a skipped command, print one dim single-line notice: e.g. `not an error (grep exit 1) — nothing to explain`. No LLM call, no cache write.
- **D-11:** Force-explain escape hatch: `?? -f` (or equivalent flag the CLI already supports / planner designs) bypasses the skip list and runs the normal explain flow. Exact flag name deferred to planner.

### Claude's Discretion
- Exact TOML key names/structure (e.g., `[skip]` table vs flat keys) — planner decides, must satisfy D-06..D-08.
- Force-explain flag name — planner decides, must satisfy D-11.
- Stderr/verbose logging conventions — reuse whatever Phase 2 CLI already uses.
</decisions>

<deferred>
## Deferred Ideas

- Exit-code ranges (e.g., `grep=1-2`) in user config.
- Regex-based matching on full command line.
- Per-project config overrides.
- Auto-learning skip patterns from user behavior.
</deferred>

<next_steps>
## Next Steps

Run `/gsd-plan-phase 4` to produce PLAN.md from these decisions.
</next_steps>
