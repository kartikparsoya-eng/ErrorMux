---
phase: 04-skip-list-filtering
plan: 01
subsystem: skip-list
tags: [skip, toml, config, filtering]
dependency_graph:
  requires: []
  provides: ["errormux.skip.should_skip", "errormux.skip.load_skip_rules", "errormux.skip.extract_command_name", "errormux.skip.BUILTIN_SKIP_RULES"]
  affects: ["src/errormux/cli.py (via Plan 04-02)"]
tech_stack:
  added: []
  patterns: ["stdlib tomllib config loader", "graceful-fallback on parse error", "module-level constant for built-ins"]
key_files:
  created:
    - src/errormux/skip.py
    - tests/test_skip.py
  modified: []
decisions:
  - "Use stdlib tomllib only — no new deps (per CLAUDE.md minimal stack)"
  - "extract_command_name uses regex ^[A-Za-z_][A-Za-z0-9_]*= to detect env assignments"
  - "load_skip_rules re-reads config each call (test isolation > caching; load is cheap)"
  - "Per-entry try/except so one malformed user rule doesn't void the rest"
metrics:
  duration: "~5 min"
  completed: "2026-04-15"
  tasks: 2
  tests: 13
requirements: [SKIP-01, SKIP-02, SKIP-03, SKIP-04]
---

# Phase 4 Plan 1: Skip Module + TOML Loader Summary

**One-liner:** Implements `errormux.skip` with built-in skip rules (grep/test/[[/[/diff at exit 1), a TOML config loader supporting additive rules and disable-list, and an `extract_command_name` helper that strips leading env assignments — pure logic module ready for CLI wiring in Plan 04-02.

## What Was Built

- `src/errormux/skip.py` (~125 lines): `BUILTIN_SKIP_RULES`, `extract_command_name`, `load_skip_rules`, `should_skip`.
- `tests/test_skip.py`: 13 unit tests covering built-ins, user add, user disable, malformed config, command-name extraction including env-prefix stripping.

## Tasks

| Task | Phase | Commit | Status |
|------|-------|--------|--------|
| 1    | RED — failing tests | `84232bb` | done |
| 2    | GREEN — implement skip.py | `98b987b` | done |

## Verification

- `uv run pytest tests/test_skip.py -v` → **13 passed in 0.02s**
- `uv run python -c "from errormux.skip import should_skip, load_skip_rules, extract_command_name"` → **OK**
- No new dependencies in `pyproject.toml` (stdlib tomllib only).

## Requirement Coverage

- **SKIP-01** grep exit 1 — covered by BUILTIN_SKIP_RULES + test.
- **SKIP-02** test/[[/[ exit 1 — covered.
- **SKIP-03** diff exit 1 — covered.
- **SKIP-04** user TOML config add + disable — covered.

Wiring into CLI short-circuit is Plan 04-02's scope.

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None.

## Self-Check: PASSED

- `src/errormux/skip.py` — FOUND
- `tests/test_skip.py` — FOUND
- commit `84232bb` — FOUND
- commit `98b987b` — FOUND
