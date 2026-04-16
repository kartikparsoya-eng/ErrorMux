---
phase: 8
plan: 1
subsystem: cache
tags: [model, cache-key, configuration]
requires: [Phase 7]
provides: [cache_key_with_model]
affects: [cache.py, cli.py, client.py]
tech-stack:
  added: []
  patterns: [model-scoped-cache-keys]
key-files:
  created: []
  modified:
    - src/errormux/client.py
    - src/errormux/cache.py
    - src/errormux/cli.py
    - tests/test_cache.py
decisions:
  - Cache key includes model name to prevent stale explanations after model switch
metrics:
  duration: 5m
  completed: 2026-04-16
  tasks: 4
  files: 4
---

# Phase 8 Plan 1: Model Constant and Cache Key Update Summary

Updated the Ollama model constant and modified cache key generation to include model name.

## One-liner

Model constant updated to gemma4:e2b with cache key generation including model parameter to prevent stale explanations.

## Tasks Completed

| Task | Description | Status |
|------|-------------|--------|
| 1 | Update model constant to gemma4:e2b | Done |
| 2 | Add cache_clear() function | Done |
| 3 | Update make_cache_key() to include model | Done |
| 4 | Update CLI to pass model to cache functions | Done |

## Changes Made

### src/errormux/client.py
- Updated `OLLAMA_MODEL` constant from `"gemma3:4b"` to `"gemma4:e2b"`

### src/errormux/cache.py
- Added `cache_clear()` function to delete all cached responses
- Updated `make_cache_key(model, cmd, stderr)` to include model parameter

### src/errormux/cli.py
- Imported `OLLAMA_MODEL` from client module
- Updated cache key call to pass model: `make_cache_key(OLLAMA_MODEL, cmd, stderr)`

### tests/test_cache.py
- Updated all `make_cache_key()` calls to include model parameter
- Added `test_cache_key_different_model()` test case

## Verification

```bash
$ uv run python -c "from errormux.cache import make_cache_key; print(make_cache_key('gemma4:e2b', 'ls', 'error'))"
e805371c68a2704f61ae2ee284b18431e7c91fab9b35413c41ef0e239628fcd4

$ uv run pytest
64 passed in 0.25s
```

## Deviations from Plan

None - plan executed exactly as written.

## Commit

- `5e41aed`: feat(08-01): update model constant and cache key
