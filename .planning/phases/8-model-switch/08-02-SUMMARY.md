---
phase: 8
plan: 2
subsystem: config
tags: [config, error-handling, model, cache-purge]
requires: [08-01]
provides: [dynamic_model_config, model_not_found_error, cache_purge_on_first_run]
affects: [config.py, client.py, cli.py, pyproject.toml]
tech-stack:
  added: [tomli]
  patterns: [config-file-generation, graceful-error-messages]
key-files:
  created:
    - src/errormux/config.py
  modified:
    - src/errormux/client.py
    - src/errormux/cli.py
    - pyproject.toml
    - tests/test_cache.py
decisions:
  - Config file at ~/.shell-explainer/config.toml documents model requirement
  - Old cache purged on first run to prevent stale explanations
  - Model not found error provides helpful ollama pull command
metrics:
  duration: 8m
  completed: 2026-04-16
  tasks: 6
  files: 5
---

# Phase 8 Plan 2: Config File and Model Error Handling Summary

Created config.toml with model documentation and added helpful error message when model not found.

## One-liner

Config module generates config.toml with model documentation, purges old cache on first run, and provides helpful error messages when model is not installed.

## Tasks Completed

| Task | Description | Status |
|------|-------------|--------|
| 1 | Create config.py module | Done |
| 2 | Add tomli dependency | Done |
| 3 | Update client to use config model | Done |
| 4 | Add model not found error handling | Done |
| 5 | Purge old cache on first run | Done |
| 6 | Update CLI to use config model | Done |

## Changes Made

### src/errormux/config.py (new)
- `ensure_config()` - Creates config file if it doesn't exist, purges old cache on first run
- `get_model_name()` - Returns model name from config file (defaults to gemma4:e2b)
- Config file documents model requirement with install command: `ollama pull gemma4:e2b`

### src/errormux/client.py
- Removed hardcoded `OLLAMA_MODEL` constant
- Imported `get_model_name` from config
- Uses dynamic model from config in `chat_with_ollama()`
- Added model not found error handling with helpful message

### src/errormux/cli.py
- Imported `get_model_name` from config instead of `OLLAMA_MODEL`
- Updated cache key call: `make_cache_key(get_model_name(), cmd, stderr)`

### pyproject.toml
- Added `tomli` dependency for TOML parsing

### tests/test_cache.py
- Added mock for `errormux.cli.get_model_name` in `test_cli_cache_hit`

## Verification

```bash
$ rm -rf ~/.shell-explainer/config.toml
$ uv run python -c "from errormux.config import ensure_config; ensure_config()"
$ cat ~/.shell-explainer/config.toml
# ErrorMux Configuration
# Generated automatically on first run

[model]
# Required: Ollama model for explanations
# Install: ollama pull gemma4:e2b
name = "gemma4:e2b"

$ uv run pytest
64 passed in 0.25s
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Test isolation for config module**
- **Found during:** Task 6 verification
- **Issue:** test_cli_cache_hit was calling real config module, causing cache mismatch
- **Fix:** Added `monkeypatch.setattr("errormux.cli.get_model_name", lambda: "gemma4:e2b")` for isolation
- **Files modified:** tests/test_cache.py
- **Commit:** 39305e7

## Commit

- `39305e7`: feat(08-02): add config file and model error handling
