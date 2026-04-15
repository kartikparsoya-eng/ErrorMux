---
quick_id: 260415-q0k
description: Fix offline graceful degradation blocker in Phase 2 UAT - add ConnectError exception handler
date: 2026-04-15
commit: d714dd7
files:
  - src/errormux/client.py
---

# Quick Task Summary: Fix Offline Graceful Degradation

## One-Liner
Added `httpx.ConnectError` exception handler to client.py, enabling proper "[explainer offline]" message when Ollama is unavailable.

## What Was Done
- Added `ConnectError` to the httpx import in `src/errormux/client.py`
- Added exception handler that catches `ConnectError` and raises `ConnectionError` with message "Ollama service unavailable"
- CLI already handles `ConnectionError` gracefully, so this enables the proper offline behavior

## Changes Made
| File | Change |
|------|--------|
| `src/errormux/client.py` | Import `ConnectError` from httpx; add exception handler |

## Verification
- Python import test passed: `uv run python -c "from errormux.client import chat_with_ollama"`
- Code compiles without errors

## Commit
- `d714dd7`: fix(260415-q0k): add ConnectError handler for offline graceful degradation
