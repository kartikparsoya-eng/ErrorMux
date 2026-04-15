---
phase: 02-cli-ollama-core
plan: 02
subsystem: cli
tags: [cli, rich, temp-files, integration]
dependencies:
  requires: [02-01]
  provides: [explain, read_context]
  affects: []
tech_stack:
  added: []
  patterns: [rich-console, temp-file-reading, error-handling]
key_files:
  created:
    - src/errormux/prompts.py
    - tests/test_prompts.py
    - tests/test_cli.py
  modified:
    - src/errormux/cli.py
decisions:
  - Shell-aware system prompt mentions zsh (D-03)
  - WHY in dim gray, FIX in bold green (D-07)
  - Graceful "[explainer offline]" on timeout/service-down (D-08)
  - Raw output for unparseable responses (D-10)
metrics:
  duration: 6 minutes
  completed_date: 2026-04-15
  test_count: 17
  coverage: prompt construction, CLI integration, error handling
---

# Phase 02 Plan 02: CLI Integration with Temp Files and Rich Output Summary

## One-Liner

CLI explain() command reads temp files, constructs prompts, calls Ollama, and displays formatted WHY/FIX output with graceful error handling.

## What Was Built

### Task 1: Prompt Construction Module

Created `src/errormux/prompts.py` with:
- `SYSTEM_PROMPT` constant - shell-aware prompt for zsh (D-03)
- Requests WHY/FIX format (D-02)
- `build_user_prompt()` function formats cmd, stderr, exit code

### Task 2: CLI explain() Implementation

Updated `src/errormux/cli.py` with:
- `read_context()` function to read temp files (CLI-01)
- Full `explain()` implementation:
  - Reads captured context from temp files
  - Builds prompt and calls Ollama
  - Prints WHY in dim gray, FIX in bold green (CLI-05, D-07)
  - Handles timeout with "[explainer offline]" (CLI-06, D-08)
  - Handles unparseable response with raw output (D-10)
  - Handles missing temp files gracefully

## Verification

All 33 tests pass:
```bash
uv run pytest tests/ -xvs
# 33 passed in 0.14s
```

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| prompts.py | 9 | system prompt content, user prompt formatting |
| cli.py | 8 | temp file reading, WHY/FIX styling, error handling |

## Deviations from Plan

None - plan executed exactly as written.

## Threat Mitigations Applied

| Threat | Mitigation | Status |
|--------|------------|--------|
| T-02-04 (Elevation of Privilege) | FIX command printed as text only, never executed | ✅ Applied in cli.py |
| T-02-05 (Tampering) | Temp files accepted as-is (single-user machine) | ✅ Accept per threat model |

## Key Artifacts

- `src/errormux/prompts.py` (25 lines) - Prompt construction
- `src/errormux/cli.py` (67 lines) - Full CLI implementation
- `tests/test_prompts.py` (65 lines) - Prompt tests
- `tests/test_cli.py` (198 lines) - CLI integration tests

## Commits

| Hash | Message |
|------|---------|
| `0907fe4` | feat(02-02): implement prompt construction module |
| `1301e91` | feat(02-02): implement CLI explain() with temp files and Rich output |

## Self-Check: PASSED

- [x] `src/errormux/cli.py` exists with explain() function
- [x] `src/errormux/prompts.py` exists with SYSTEM_PROMPT
- [x] All 33 tests pass
- [x] Commits exist in git history

## Phase 2 Complete

Both plans executed successfully. The CLI now:
1. Reads captured command context from temp files
2. Calls Ollama localhost:11434 with structured prompts
3. Streams and buffers responses
4. Displays formatted WHY (dim) and FIX (bold green) output
5. Gracefully handles timeout, service-down, and unparseable responses
