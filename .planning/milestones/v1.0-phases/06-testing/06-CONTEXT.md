# Phase 6: Testing - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Comprehensive pytest test suite for ErrorMux components: cache hit/miss logic, skip-list filtering, prompt construction, and mocked Ollama calls. Tests must achieve 80% code coverage measured by pytest-cov.

**In scope:** pytest tests for all modules, httpx MockTransport for Ollama mocking, coverage measurement and enforcement.
**Out of scope:** Integration tests requiring live Ollama service, performance benchmarks, zsh plugin tests.
</domain>

<decisions>
## Implementation Decisions

### Coverage Target
- **D-01:** 80% code coverage required — standard industry threshold, allows for hard-to-test edge cases while ensuring core paths are verified.

### TEST-04 Compliance
- **D-02:** Switch to httpx MockTransport for Ollama mocking — strict compliance with TEST-04 requirement, tests real httpx transport layer rather than mocking at the ollama SDK level.

### Coverage Tooling
- **D-03:** Add pytest-cov to dev dependencies — enables coverage reports (`uv run pytest --cov=errormux`), CI integration, and threshold enforcement.

### Claude's Discretion
- Exact coverage report format (terminal, HTML, or both)
- Whether to fail CI on coverage threshold miss
- Test organization (per-module files vs unified test files)
- Handling of untestable code paths (e.g., zsh integration)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Context
- `.planning/PROJECT.md` — Project vision, constraints (Python 3.12, uv, minimal dependencies)
- `.planning/REQUIREMENTS.md` — TEST-01, TEST-02, TEST-03, TEST-04 acceptance criteria
- `.planning/research/STACK.md` — pytest usage, testing conventions

### Prior Phase Context
- `.planning/phases/02-cli-ollama-core/02-CONTEXT.md` — CLI flow, Ollama client interface
- `.planning/phases/03-cache-system/03-CONTEXT.md` — Cache module, SQLite schema
- `.planning/phases/04-skip-list-filtering/04-CONTEXT.md` — Skip module, config loading

</canonical_refs>

<code_context>
## Existing Code Insights

### Existing Test Files
- `tests/test_cache.py` — 10 tests covering cache hit/miss, TTL, key generation
- `tests/test_skip.py` — 11 tests covering skip rules, config loading, command extraction
- `tests/test_prompts.py` — 10 tests covering SYSTEM_PROMPT and build_user_prompt
- `tests/test_cli.py` — 18 tests covering CLI explain flow, skip integration, error handling
- `tests/test_parser.py` — 10 tests covering response parsing
- `tests/test_client.py` — 6 tests covering Ollama client (uses unittest.mock — needs conversion to httpx MockTransport)

### Current Test Status
- 63 tests pass in 0.26s
- No coverage measurement currently (pytest-cov not installed)
- TEST-04 uses `unittest.mock.patch` instead of httpx MockTransport

### Modules Under Test
- `src/errormux/cli.py` — CLI entry point, explain command
- `src/errormux/cache.py` — SQLite cache operations
- `src/errormux/skip.py` — Skip-list filtering logic
- `src/errormux/prompts.py` — Prompt construction
- `src/errormux/parser.py` — Response parsing
- `src/errormux/client.py` — Ollama client wrapper

### Integration Points
- pytest configuration in `pyproject.toml`
- Test discovery: `tests/` directory
- Run command: `uv run pytest`

</code_context>

<specifics>
## Specific Ideas

- Add pytest-cov to pyproject.toml dev dependencies
- Convert test_client.py from unittest.mock to httpx MockTransport
- Add coverage threshold check: `uv run pytest --cov=errormux --cov-fail-under=80`
- Document coverage run in README or CLAUDE.md

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 06-testing*
*Context gathered: 2026-04-15*
