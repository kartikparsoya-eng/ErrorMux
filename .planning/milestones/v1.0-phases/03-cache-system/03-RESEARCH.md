# Phase 3: Cache System - Research

**Researched:** 2026-04-15
**Phase:** 03-cache-system

---

## Problem Statement

Implement SQLite caching for LLM explanations to achieve instant (sub-100ms) responses on repeated errors, with 7-day TTL and SHA256-based cache keys.

---

## Technical Analysis

### Cache Key Strategy

**Requirement:** SHA256(cmd+stderr) for accuracy

```python
import hashlib

def make_cache_key(cmd: str, stderr: str) -> str:
    return hashlib.sha256(f"{cmd}|{stderr}".encode()).hexdigest()
```

**Why SHA256:**
- Cryptographic hash ensures different stderr produces different key
- 64 hex characters, constant length, URL-safe
- No collision concerns for this use case

### SQLite Schema

**Per D-02 (minimal schema):**

```sql
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    response TEXT NOT NULL,
    created_at REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_created_at ON cache(created_at);
```

**Notes:**
- `key` is SHA256 hash (TEXT PRIMARY KEY)
- `response` stores full WHY/FIX text
- `created_at` is Unix timestamp (REAL) for easy TTL math

### TTL Enforcement

**Two approaches:**

1. **Lazy cleanup on read:** Check TTL on every read, delete expired entries
   - Pros: Simple, no background process
   - Cons: Expired entries persist until read

2. **Periodic cleanup:** Run cleanup on every N reads or on CLI start
   - Pros: Keeps cache size bounded
   - Cons: More complex

**Recommendation:** Lazy cleanup (per D-02, D-04 decisions). Delete expired entry when encountered during read. Optionally run bulk cleanup on CLI startup.

### Cache Location

**Requirement:** `~/.shell-explainer/cache.db` (per CLI-02)

```python
from pathlib import Path

CACHE_DIR = Path.home() / ".shell-explainer"
CACHE_DB = CACHE_DIR / "cache.db"

# Ensure directory exists
CACHE_DIR.mkdir(parents=True, exist_ok=True)
```

### Connection Handling

**Options:**

1. **Per-call connection:** Open/close on every cache operation
   - Pros: Simple, no state management
   - Cons: Connection overhead (~1-2ms)

2. **Singleton connection:** Reuse connection across calls
   - Pros: Faster operations
   - Cons: Need to manage connection lifecycle

**Recommendation:** Per-call connection. For single CLI invocation (one lookup, maybe one write), the overhead is negligible. Simpler code.

### Integration Flow

**Per D-04 (check cache before prompt build):**

```
1. read_context() → cmd, stderr, exit_code
2. key = make_cache_key(cmd, stderr)
3. cached = cache_get(key)
4. if cached and not expired:
      print cached response
      exit 0
5. # Cache miss - proceed with Ollama call
6. user_prompt = build_user_prompt(cmd, stderr, exit_code)
7. response = chat_with_ollama(...)
8. why, fix = parse_response(response)
9. cache_set(key, f"WHY: {why}\nFIX: {fix}")
10. print WHY/FIX with Rich
```

---

## Validation Architecture

### Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Quick run | `uv run pytest tests/ -x -q` |
| Full suite | `uv run pytest tests/ -v` |

### Per-Task Verification Map

| Task ID | Plan | Requirement | Test Type | Automated Command |
|---------|------|-------------|-----------|-------------------|
| 03-01-01 | 01 | CLI-02 | unit | `uv run pytest tests/test_cache.py::test_cache_key -xvs` |
| 03-01-02 | 01 | CLI-02 | unit | `uv run pytest tests/test_cache.py::test_cache_set_get -xvs` |
| 03-01-03 | 01 | CLI-03 | unit | `uv run pytest tests/test_cache.py::test_cache_hit -xvs` |
| 03-02-01 | 02 | CLI-03 | integration | `uv run pytest tests/test_cache.py::test_cli_cache_integration -xvs` |

### Test Doubles Strategy

```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path

@pytest.fixture
def temp_cache_db():
    """Create temp cache DB for isolated testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir) / "test-cache.db"
```

---

## Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Cache directory doesn't exist | `mkdir(parents=True, exist_ok=True)` |
| SQLite locking on concurrent access | Single-user CLI, no concurrency concerns |
| Large stderr causes large key | SHA256 always produces 64-char key |
| Response format changes | Store raw text, parse on read |
| TTL check off by one day | Use `time.time() - created_at > 7 * 86400` |

---

## Reusable Assets

- `src/errormux/cli.py` — `explain()` function to modify
- `src/errormux/client.py` — `chat_with_ollama()` to call on miss
- `src/errormux/parser.py` — `parse_response()` to validate before caching

---

## Implementation Notes

1. **New module:** `src/errormux/cache.py` — cache operations
2. **Modify:** `src/errormux/cli.py` — integrate cache check
3. **Test file:** `tests/test_cache.py` — cache unit tests

---

*Research complete: 2026-04-15*
