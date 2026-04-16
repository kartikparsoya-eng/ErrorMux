---
phase: 02-cli-ollama-core
plan: 01
subsystem: client
tags: [ollama, streaming, parsing, tdd]
dependencies:
  requires: []
  provides: [chat_with_ollama, parse_response]
  affects: [cli.py]
tech_stack:
  added: [ollama>=0.6.1]
  patterns: [streaming-response, error-handling, regex-parsing]
key_files:
  created:
    - src/errormux/client.py
    - src/errormux/parser.py
    - tests/test_client.py
    - tests/test_parser.py
  modified:
    - pyproject.toml
decisions:
  - Use ollama SDK with streaming enabled (D-04)
  - 10s timeout on all requests (D-09)
  - Graceful error handling with "[explainer offline]" (D-08)
  - Case-insensitive WHY/FIX parsing (D-02)
metrics:
  duration: 8 minutes
  completed_date: 2026-04-15
  test_count: 16
  coverage: client streaming, timeout, service-down, parsing edge cases
---

# Phase 02 Plan 01: Ollama Client Wrapper + Response Parsing Summary

## One-Liner

Ollama client wrapper with streaming, 10s timeout, graceful error handling, and WHY/FIX response parser with case-insensitive regex matching.

## What Was Built

### Task 1: Ollama Client Wrapper

Created `src/errormux/client.py` with:
- `chat_with_ollama()` function that streams from Ollama and buffers full response
- Constants: `OLLAMA_HOST` (localhost:11434), `OLLAMA_TIMEOUT` (10.0s), `OLLAMA_MODEL` (gemma3:4b)
- Error handling: `TimeoutException` → `TimeoutError`, `ResponseError` → `ConnectionError`
- Added `ollama>=0.6.1` dependency to pyproject.toml

### Task 2: Response Parser

Created `src/errormux/parser.py` with:
- `ParseError` custom exception
- `parse_response()` function using case-insensitive regex to extract WHY/FIX sections
- `format_output()` utility function for display formatting
- Handles multi-line WHY text, extra whitespace, and mixed case labels

## Verification

All 16 tests pass:
```bash
uv run pytest tests/ -xvs
# 16 passed in 0.18s
```

### Test Coverage

| Module | Tests | Coverage |
|--------|-------|----------|
| client.py | 6 | streaming, timeout, service-down, model/messages format |
| parser.py | 10 | standard format, multi-line, malformed, whitespace, case |

## Deviations from Plan

None - plan executed exactly as written.

## Threat Mitigations Applied

| Threat | Mitigation | Status |
|--------|------------|--------|
| T-02-01 (Elevation of Privilege) | FIX command only displayed as text, never executed | ✅ Applied in parser (returns string only) |

## Key Artifacts

- `src/errormux/client.py` (40 lines) - Ollama client wrapper
- `src/errormux/parser.py` (38 lines) - WHY/FIX parser
- `tests/test_client.py` (95 lines) - Client tests
- `tests/test_parser.py` (77 lines) - Parser tests

## Commits

| Hash | Message |
|------|---------|
| `68ab4dd` | test(02-01): add failing tests for Ollama client wrapper |
| `b76c113` | feat(02-01): implement WHY/FIX response parser |

## Next Steps

Plan 02-02 will:
- Create `prompts.py` with system/user prompt construction
- Update `cli.py` to wire everything together with Rich output
