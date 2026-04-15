# Project Research Summary

**Project:** ErrorMux
**Domain:** zsh plugin with Python CLI backend + Ollama local LLM integration
**Researched:** 2026-04-15
**Confidence:** HIGH

## Executive Summary

ErrorMux is a zsh plugin that provides instant, AI-powered explanations for shell command failures using a local LLM (Ollama). Unlike existing solutions like thefuck (rule-based) or ai-shell (cloud-dependent), ErrorMux differentiates through offline-first design, intelligent caching, and smart false-positive filtering. The recommended architecture uses a two-layer approach: zsh hooks capture command context (preexec/precmd) and a Python CLI (typer + rich) handles cache lookup and Ollama integration.

Key risks center on shell hook reliability (race conditions, stderr capture) and Ollama latency. These are mitigated through: (1) using `_functions` array pattern for hook registration to avoid plugin conflicts, (2) storing captured state in prefixed global variables cleared atomically by the `??` widget, and (3) implementing a SQLite cache with 7-day TTL to ensure sub-100ms responses for repeated errors. The skip-list is critical—commands like grep, test, and diff exit 1 semantically, not as errors, and must be filtered before calling the LLM.

## Key Findings

### Recommended Stack

The modern Python CLI stack: **Python 3.12+** for async optimizations, **uv** as the package manager (10-100x faster than pip/poetry), **ollama SDK** (0.6.1) for clean LLM integration with built-in streaming and error handling, **typer** for CLI with automatic help generation, and **rich** for beautiful terminal output. SQLite (stdlib) handles caching with zero configuration.

**Core technologies:**
- **Python 3.12+**: Runtime — modern async support, performance improvements
- **uv**: Package manager — replaces pip/poetry, handles Python version management
- **ollama SDK 0.6.1**: LLM client — typed responses, streaming, built on httpx
- **typer**: CLI framework — Click + type hints + Rich integration, minimal boilerplate
- **SQLite**: Cache storage — zero-config, single-file, stdlib included

### Expected Features

Market analysis reveals clear feature categories. ErrorMux's competitive moat is **offline-first local LLM** combined with **cache-backed speed** and **skip-list for false positives**—no other tool offers this combination.

**Must have (table stakes):**
- Command capture via preexec/precmd hooks — users expect tool to know what failed
- Exit code + stderr awareness — essential diagnostic context
- On-demand trigger (`??`) — not auto-on-every-error (explicitly rejected as anti-feature)
- Fast response — sub-100ms cached, <10s fresh

**Should have (competitive):**
- Local LLM (offline-first) — unmatched in market, core differentiator
- SQLite cache (7-day TTL) — instant for repeated errors
- Skip-list filtering — unique feature, avoids noise from grep/test/diff
- Structured output (WHY + FIX) — one sentence each, actionable

**Defer (v2+):**
- Config file and custom skip-list patterns — add after validation
- Multi-model support and bash compatibility — future consideration

### Architecture Approach

Two-layer architecture: zsh plugin layer handles state capture via hooks; Python CLI layer handles orchestration, caching, and LLM calls. Data flows: preexec captures command → precmd captures exit/stderr → `??` widget invokes CLI → cache check → Ollama call → Rich output.

**Major components:**
1. **errormux.plugin.zsh** — Entry point, hook registration (using `_functions` array), widget binding, state capture
2. **Python CLI (cli.py)** — typer entry point, orchestrates cache lookup → skip-list → prompt construction → Ollama call
3. **Cache layer (cache.py)** — SQLite with SHA256(command + exit_code + stderr) key, 7-day TTL enforcement
4. **Skip-list (skip_list.py)** — Filters grep, test, [, diff, find exit 1 before LLM call
5. **Ollama client (ollama.py)** — 10s timeout, streaming response, graceful degradation

### Critical Pitfalls

Top pitfalls that will cause failure if not addressed:

1. **Hook race condition** — preexec and precmd are independent calls; stale state if user runs commands between failure and `??`. Prevent with: global vars cleared atomically by widget, timestamp validation optional.
2. **Ollama timeout blocks shell** — 10s freeze feels like crash. Prevent with: explicit timeout, "Thinking..." feedback, graceful error message.
3. **Skip-list false positives** — grep exit 1 = "no match", not error. Prevent with: hardcoded patterns for grep/test/diff/find, check BEFORE LLM call.
4. **Cache poisoning** — Same command, different stderr = wrong cached explanation. Prevent with: include stderr in SHA256 key, not just command + exit code.
5. **Hook pollution breaks other plugins** — Defining `preexec()` overwrites other hooks. Prevent with: use `preexec_functions+=()` array pattern.
6. **Python dependency hell** — Missing httpx/typer/rich = import errors. Prevent with: uv for isolation, install script checks Python version.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Capture Layer (zsh Plugin Infrastructure)
**Rationale:** Foundation—everything depends on capturing command context correctly. Must address hook race conditions and pollution upfront.
**Delivers:** Working preexec/precmd hooks, `??` widget stub, global state capture
**Addresses:** Command capture, exit code awareness, stderr capture (from FEATURES.md)
**Avoids:** Hook race condition, hook pollution (from PITFALLS.md)
**Key pattern:** `preexec_functions+=()` and `precmd_functions+=()` array pattern

### Phase 2: Python CLI + Ollama Integration
**Rationale:** Core value—LLM explanation. Need working CLI before cache/skip-list make sense.
**Delivers:** typer CLI, prompt construction, Ollama API calls, Rich output formatting
**Uses:** typer, rich, ollama SDK (from STACK.md)
**Implements:** Python backend layer (from ARCHITECTURE.md)
**Avoids:** Ollama timeout (10s limit, "Thinking..." feedback)

### Phase 3: SQLite Cache System
**Rationale:** Performance—cache makes repeated errors instant. Cache depends on command capture working.
**Delivers:** SQLite database, SHA256 key generation, 7-day TTL, lookup/store operations
**Uses:** Python sqlite3 stdlib (from STACK.md)
**Avoids:** Cache poisoning (include stderr in key)

### Phase 4: Skip-List Implementation
**Rationale:** UX quality—without skip-list, grep/test/diff "failures" produce useless explanations. Can be added after basic flow works.
**Delivers:** Pattern matching for grep, test, [, diff, find; checked before LLM call
**Avoids:** Skip-list false positives
**Test corpus:** 50+ common commands with non-error exit codes

### Phase 5: Installation + Polish
**Rationale:** User experience—one-command install, dependency checks, .zshrc sourcing.
**Delivers:** install.sh with uv/pip fallback, Python version check, plugin sourcing
**Avoids:** Python dependency hell
**Verification:** Fresh VM install test

### Phase Ordering Rationale

- **Phase 1 first** because all other phases depend on captured command context—can't cache or explain without knowing what failed
- **Phase 2 before cache/skip-list** because you need working LLM integration to test caching and filtering
- **Phase 3 before Phase 4** because cache provides immediate value; skip-list is quality polish
- **Phase 5 last** because install script needs all components working to test

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Ollama Integration):** Prompt engineering for WHY/FIX structure—may need iteration to get gemma3:4b producing clean one-sentence outputs
- **Phase 4 (Skip-List):** Edge case discovery—test corpus development may reveal patterns not in initial list

Phases with standard patterns (skip research-phase):
- **Phase 1 (Capture Layer):** Well-documented zsh hook patterns, zsh-autosuggestions and thefuck provide reference implementations
- **Phase 3 (Cache):** SQLite patterns are standard, cache key strategy is clear from research

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All technologies verified with official docs Apr 2026 |
| Features | HIGH | Competitor analysis thorough, clear differentiation path |
| Architecture | HIGH | Reference implementations exist (thefuck, zsh-autosuggestions) |
| Pitfalls | MEDIUM | Sources are official docs + community, no Context7 verification available |

**Overall confidence:** HIGH

### Gaps to Address

- **Prompt engineering:** Research doesn't specify exact prompt for WHY/FIX structure—will need iterative testing during Phase 2 planning
- **Stderr capture reliability:** Temp file pattern has edge cases (concurrent commands, background jobs)—validate during Phase 1 implementation
- **Skip-list completeness:** Initial list may miss edge cases—plan for user-configurable patterns in v1.x

## Sources

### Primary (HIGH confidence)
- uv docs (docs.astral.sh/uv) — Package manager, verified Apr 2026
- ollama-python GitHub — Official SDK, verified Apr 2026
- typer docs (typer.tiangolo.com) — CLI framework, verified Apr 2026
- rich docs (rich.readthedocs.io) — Terminal output, verified Apr 2026
- Ollama API docs (github.com/ollama/ollama/docs/api.md) — REST API reference

### Secondary (MEDIUM confidence)
- Zsh Functions Manual (zsh.sourceforge.io) — Hook function arrays pattern
- thefuck GitHub (96.5k stars) — Reference implementation for shell integration
- zsh-autosuggestions — Reference for hook registration pattern
- Oh My Zsh plugin standard — Plugin conventions

### Tertiary (Community sources)
- Oh My Zsh FAQ — Common zsh plugin issues
- Zinit Documentation — Plugin manager patterns

---
*Research completed: 2026-04-15*
*Ready for roadmap: yes*
