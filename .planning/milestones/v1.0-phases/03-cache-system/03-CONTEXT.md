# Phase 3: Cache System - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

SQLite cache that stores LLM explanations keyed by SHA256(cmd+stderr), with 7-day TTL, returning cached responses instantly on repeat errors. Cache check happens before prompt construction to achieve sub-100ms response time.

</domain>

<decisions>
## Implementation Decisions

### Cache Indicator
- **D-01:** Silent cache indicator — no visual feedback when response is from cache (seamless UX)

### Table Schema
- **D-02:** Minimal schema: `key` (SHA256 hash), `response` (WHY/FIX text), `created_at` (timestamp for TTL)

### Error Caching
- **D-03:** Don't cache errors — only cache successful WHY/FIX parses. Timeout/failure cases retry on next occurrence.

### Integration Point
- **D-04:** Check cache before prompt build — immediate lookup after reading temp files, skip prompt construction + Ollama call on hit

### Claude's Discretion
- Exact SQLite connection handling (singleton vs per-call)
- TTL enforcement approach (check on read vs lazy cleanup)
- Whether to store WHY/FIX separately or as single response text

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project vision, constraints (SQLite, 7-day TTL, sub-100ms cached response)
- `.planning/REQUIREMENTS.md` — CLI-02, CLI-03 requirements
- `.planning/research/STACK.md` — SQLite usage patterns, TTL implementation

### Prior Phase Context
- `.planning/phases/02-cli-ollama-core/02-CONTEXT.md` — CLI flow, prompt building, Ollama client
- `.planning/phases/01-capture-layer/01-CONTEXT.md` — Temp file locations

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `src/errormux/cli.py` — `explain()` command, `read_context()` function — integrate cache check here
- `src/errormux/client.py` — `chat_with_ollama()` function — call only on cache miss
- `src/errormux/parser.py` — `parse_response()` function — use to validate before caching

### Established Patterns
- CLI entry point: `errormux explain`
- Temp files: `/tmp/shell-explainer-last-{cmd,stderr,exit}`
- WHY/FIX output: dim gray WHY, bold green FIX via Rich Console

### Integration Points
- Cache check: after `read_context()`, before `build_user_prompt()`
- Cache write: after successful `parse_response()`, before printing output
- Cache location: `~/.shell-explainer/cache.db` (per CLI-02)

</code_context>

<specifics>
## Specific Ideas

- Use Python stdlib `sqlite3` module (zero extra dependency)
- Cache key: `hashlib.sha256(f"{cmd}|{stderr}".encode()).hexdigest()`
- TTL check: `created_at > now - 7 days` on read
- Cache directory created on first use if not exists

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-cache-system*
*Context gathered: 2026-04-15*
