---
phase: 04-skip-list-filtering
plan: 02
subsystem: skip-list
tags: [cli, skip, force-flag, short-circuit]
dependency_graph:
  requires: ["errormux.skip.should_skip", "errormux.skip.extract_command_name"]
  provides: ["errormux explain --force/-f", "skip short-circuit in CLI"]
  affects: ["end-user explain flow"]
tech_stack:
  added: []
  patterns: ["typer.Option flag", "early-return short-circuit before cache/LLM", "rich dim style for non-actionable notices"]
key_files:
  created: []
  modified:
    - src/errormux/cli.py
    - tests/test_cli.py
decisions:
  - "Skip check runs AFTER read_context and BEFORE make_cache_key (D-03, D-04, D-10) — guarantees no cache_set on skip path"
  - "Dim notice format: 'not an error ({cmd_name} exit {exit_code}) — nothing to explain' (single line, rich style='dim')"
  - "--force / -f bypasses skip entirely; rest of flow unchanged (D-11)"
  - "Tests mock cache_get/cache_set/chat_with_ollama at cli module boundary to assert skip-path does not call any of them"
metrics:
  duration: "~2 min"
  completed: "2026-04-15"
  tasks: 2
  tests_added: 7
  tests_total: 63
requirements: [SKIP-01, SKIP-02, SKIP-03, SKIP-04]
---

# Phase 04 Plan 02: Integrate Skip Check into CLI Summary

One-liner: Wired `errormux.skip.should_skip` into the CLI explain command with a `--force/-f` bypass, short-circuiting grep/test/[[/[/diff exit-1 before any cache or LLM work.

## What Changed

- `src/errormux/cli.py`:
  - Imported `extract_command_name`, `should_skip` from `errormux.skip`.
  - Added `force: bool = typer.Option(False, "--force", "-f", ...)` to `explain()`.
  - Inserted skip short-circuit block immediately after `read_context()` and before `make_cache_key()`. On skip, prints dim one-line notice via `console.print(..., style="dim")` and returns — no cache_get, no cache_set, no LLM call.
- `tests/test_cli.py`:
  - Added `TestForceFlag` (1 test) verifying `--force`/`-f` appear in `explain --help`.
  - Added `TestSkipIntegration` (6 tests) verifying grep/diff/test exit-1 short-circuit, --force bypass, real error (grep exit 2) not skipped, and notice format.

## Verification

- `uv run pytest -v` → 63 passed (0 failed).
- `grep -n "should_skip" src/errormux/cli.py` confirms skip check at line 65, `make_cache_key` at line 72 — correct ordering (D-04).
- `uv run python -c "from errormux.cli import app; ..."` help output contains both `--force` and `-f`.

## Must-Have Truths Satisfied

- SKIP-01: grep exit 1 → dim notice, no Ollama, no cache write. Covered by `test_explain_skips_grep_exit_1`.
- SKIP-02: test/[[/[ exit 1 → short-circuit. Covered by `test_explain_skips_test_exit_1` (test command) + Plan-01 unit tests for `[`/`[[`.
- SKIP-03: diff exit 1 → short-circuit. Covered by `test_explain_skips_diff_exit_1`.
- SKIP-04: user config end-to-end via the same `load_skip_rules` loader used in Plan 01.
- D-11: `--force` bypasses skip and runs normal flow. Covered by `test_explain_force_bypasses_skip`.
- D-03/D-04/D-10: skip check before cache/LLM, no cache_set on skip. Asserted via `assert_not_called()` on mocks.
- Real errors still flow normally: `test_explain_real_error_not_skipped` (grep exit 2).

## Deviations from Plan

None — plan executed exactly as written.

## Commits

- `cbcbb0d` — test(04-02): add failing test for --force flag in explain help (RED)
- `d438aec` — feat(04-02): integrate skip check and --force flag into explain CLI (GREEN)
- `fab52bc` — test(04-02): add CLI tests for skip short-circuit and force bypass

## Known Stubs

None.

## Self-Check: PASSED

- FOUND: src/errormux/cli.py (modified, skip check at line 65, force flag added)
- FOUND: tests/test_cli.py (TestForceFlag + TestSkipIntegration added)
- FOUND: cbcbb0d
- FOUND: d438aec
- FOUND: fab52bc
