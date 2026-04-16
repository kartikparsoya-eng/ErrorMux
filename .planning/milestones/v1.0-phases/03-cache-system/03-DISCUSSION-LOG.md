# Phase 3: Cache System - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-15
**Phase:** 03-cache-system
**Areas discussed:** Cache indicator, Table schema, Error caching, Integration point

---

## Cache indicator

| Option | Description | Selected |
|--------|-------------|----------|
| Silent (no indicator) | Seamless UX, no visual noise | ✓ |
| `[cached]` prefix before WHY | Clear feedback, user knows source | |
| Dim `[cached]` after FIX line | Visible but unobtrusive | |

**User's choice:** Silent (no indicator)
**Notes:** Goal is instant explanation without interrupting flow. User doesn't need to know the source.

---

## Table schema

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal: `key`, `response`, `created_at` | Simple schema, fast lookups | ✓ |
| Add `exit_code` | Helps debug why certain errors cached | |
| Add `model_version` | Can invalidate cache if model changes | |
| Add `hit_count` | Useful for cache stats/debugging | |

**User's choice:** Minimal schema (key, response, created_at)
**Notes:** Keeps it simple; Phase 6 testing covers correctness.

---

## Error caching

| Option | Description | Selected |
|--------|-------------|----------|
| Don't cache errors | Cache only valid explanations, retry on transient failures | ✓ |
| Cache unparseable responses | Avoids repeated calls for same malformed output | |
| Cache timeout/connection failures | Retry without hitting Ollama on service down | |
| Cache all errors | Maximum cache efficiency | |

**User's choice:** Don't cache errors (only cache successful parses)
**Notes:** Timeout/failure cases should retry since Ollama might recover. Unparseable responses are rare.

---

## Integration point

| Option | Description | Selected |
|--------|-------------|----------|
| Before prompt build | Skip unnecessary work on cache hit, faster response | ✓ |
| After prompt build | Consistent flow, prompt always built | |

**User's choice:** Before prompt build (check cache first)
**Notes:** Achieves sub-100ms cached responses per CLI-03. Immediate lookup after reading temp files.

---

## Claude's Discretion

- Exact SQLite connection handling (singleton vs per-call)
- TTL enforcement approach (check on read vs lazy cleanup)
- Whether to store WHY/FIX separately or as single response text

## Deferred Ideas

None — discussion stayed within phase scope.
