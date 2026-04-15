---
phase: 03
slug: cache-system
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-04-15"
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pyproject.toml` (tool.pytest) |
| **Quick run command** | `uv run pytest tests/ -x -q` |
| **Full suite command** | `uv run pytest tests/ -v` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x -q`
- **After every plan wave:** Run `uv run pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 3 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | CLI-02 | N/A | SHA256 hash of cmd+stderr | unit | `uv run pytest tests/test_cache.py::test_cache_key -xvs` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | CLI-02 | N/A | SQLite set/get operations | unit | `uv run pytest tests/test_cache.py::test_cache_set_get -xvs` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | CLI-03 | N/A | TTL expiration check | unit | `uv run pytest tests/test_cache.py::test_cache_ttl -xvs` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | CLI-03 | N/A | Cache hit returns instantly | integration | `uv run pytest tests/test_cache.py::test_cli_cache_integration -xvs` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_cache.py` — cache key, set/get, TTL tests
- [ ] `tests/conftest.py` — shared fixtures (temp_cache_db) — already exists from Phase 2

*Existing pytest infrastructure from Phase 1 (pyproject.toml has pytest>=8.0)*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Sub-100ms cache hit | CLI-03 | Timing varies by system | 1. Run failing command 2. Type `??` 3. Run again 4. Type `??` 5. Second response should be instant |

*Primary behaviors have automated verification. Timing test is optional integration test.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 3s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
