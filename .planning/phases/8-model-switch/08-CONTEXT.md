# Phase 8: Model Switch — Context

## Problem Statement

Switch the Ollama model from gemma3:4b to gemma4:e2b, update cache key generation to include model name, and document the model requirement for users.

## Current State

### Code Locations

| File | Line | Current | Issue |
|------|------|---------|-------|
| `src/errormux/client.py` | 10 | `OLLAMA_MODEL = "gemma3:4b"` | Hardcoded old model |
| `src/errormux/cache.py` | 15 | `f"{cmd}|{stderr}"` | Cache key lacks model name |
| N/A | — | No config file | Model requirement not documented |

### Existing Behavior

- Cache stored at `~/.shell-explainer/cache.db`
- Cache TTL: 7 days (PROJECT.md)
- No config file exists

## Decisions

### D-01: Cache Migration — Purge All

**Decision:** Purge all existing cache entries when upgrading.

**Rationale:**
- Old cache keys use `f"{cmd}|{stderr}"` without model name
- New keys will include model name, so old entries become orphaned
- Clean slate guarantees fresh explanations with new model
- Simplicity outweighs attempting to migrate orphaned data

**Implementation:** Add `cache_clear()` function and call it once on first run with new model.

---

### D-02: Config File — Create config.toml

**Decision:** Create `~/.shell-explainer/config.toml` with model documentation.

**Rationale:**
- Enables future config expansion (timeout, model variants, cache TTL)
- Clear location for users to check model requirement
- Professional pattern for user-facing configuration

**Structure:**
```toml
# ErrorMux Configuration
# Generated automatically on first run

[model]
# Required: Ollama model for explanations
# Install: ollama pull gemma4:e2b
name = "gemma4:e2b"
```

---

### D-03: Model Availability — Hard Fail

**Decision:** Hard fail with helpful message when model not found.

**Rationale:**
- Forces explicit model install (no ambiguity)
- Prevents confusion about which model is being used
- Cache consistency (all responses from same model)

**Error Message:**
```
Model gemma4:e2b not found.
Run: ollama pull gemma4:e2b
```

---

### D-04: Cache Key — Include Model Name

**Decision:** Change cache key to `f"{model}|{cmd}|{stderr}"`.

**Rationale:**
- Per PROJECT.md: "Cache key must include model name to prevent stale explanations"
- Ensures fresh explanations after model switch
- Prevents returning cached responses from different model

**Implementation:**
```python
def make_cache_key(model: str, cmd: str, stderr: str) -> str:
    return hashlib.sha256(f"{model}|{cmd}|{stderr}".encode()).hexdigest()
```

---

## Success Criteria Mapping

| ID | Criteria | Decision | Implementation |
|----|----------|----------|----------------|
| MODL-01 | Plugin calls gemma4:e2b via Ollama | D-02, D-03 | Update `OLLAMA_MODEL` constant |
| MODL-02 | Cache keys include model name | D-04 | Add `model` param to `make_cache_key()` |
| MODL-03 | Config file documents model requirement | D-02 | Create config.toml on first run |

## Implementation Plan Overview

1. Update `OLLAMA_MODEL` constant to `"gemma4:e2b"`
2. Add `model` parameter to `make_cache_key()` and update callers
3. Add `cache_clear()` function to purge old cache
4. Create config.toml with model documentation on first run
5. Add model-not-found error handling with helpful message

## Dependencies

- Phase 7 (Widget Auto-Return Fix) — Complete ✓
- Ollama must be running with `gemma4:e2b` model pulled

## Risks

| Risk | Mitigation |
|------|------------|
| Users won't have gemma4:e2b | Clear error message with install command |
| Existing cache entries stale | Purge all on first run |
| Config file permissions | Use same pattern as cache directory |

---

*Context gathered: 2026-04-16*
*Decisions confirmed by user*
