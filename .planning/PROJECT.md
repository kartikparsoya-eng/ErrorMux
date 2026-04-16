# ErrorMux

## What This Is

A zsh plugin that explains shell command failures on-demand. When a command fails, pressing `Ctrl+X ?` triggers a local Gemma model (via Ollama) to provide a one-sentence explanation and a suggested fix. Cache-backed for speed, offline-first, zero cloud dependency.

## Core Value

Fast, local, on-demand error explanations that don't interrupt your flow — only when you ask for them.

## Requirements

### Validated

- ✓ zsh capture layer hooks stderr, exit code, and command text for every interactive command — v1.0
- ✓ `??` widget reads captured data and invokes Python CLI — v1.0
- ✓ Python CLI checks SQLite cache (7-day TTL) before calling Ollama — v1.0
- ✓ Ollama returns structured WHY/FIX output, streamed via Rich — v1.0
- ✓ Skip-list filters out false-positive "errors" (grep exit 1, test/[[, diff exit 1) — v1.0
- ✓ Install script sets up plugin, Python deps, and .zshrc sourcing — v1.0
- ✓ Test suite covers cache, skip-list, and prompt construction — v1.0 (92% coverage)

### Active

(None — plan next milestone)

### Out of Scope

- Auto-printing on every error (opt-in via `??` only)
- Cloud fallback or remote LLM APIs
- Multi-shell support (zsh only, no bash/fish)
- GUI or TUI beyond the single `??` output

## Context

- **Shipped:** v1.0 MVP on 2026-04-16
- **LOC:** 432 lines Python
- **Test coverage:** 92% (63 tests passing)
- Ollama runs locally at localhost:11434 with gemma3:4b
- Python 3.12 with `uv` for dependency management (httpx, typer, rich)
- zsh plugin uses preexec/precmd hooks for capture
- Cache stored at `~/.shell-explainer/cache.db`
- Config at `~/.shell-explainer/config.toml`

## Constraints

- **Stack**: Python 3.12, uv, httpx, typer, rich, SQLite — minimal dependencies
- **Model**: gemma3:4b via Ollama localhost:11434 (hard requirement)
- **Timeout**: 10s max for Ollama requests; graceful degradation on failure
- **Shell**: zsh only — leverages zsh-specific hook mechanisms

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Cache TTL: 7 days | Balances staleness risk with cache utility | ✓ Good |
| Concurrency: Block on in-flight request | Simplest implementation, avoids race conditions | ✓ Good |
| Plugin name: errormux | Matches directory name, shorter than shell-explainer | ✓ Good |
| SQLite for cache | Local, zero-config, fast lookups by SHA256 key | ✓ Good |
| httpx MockTransport for testing | Strict TEST-04 compliance, tests real transport layer | ✓ Good |
| pytest-cov 80% threshold | Industry standard, catches uncovered paths | ✓ Good (92% achieved) |
| Ctrl+X ? binding | Avoids zsh glob conflicts with ?? | ✓ Good |

---

*Last updated: 2026-04-16 after v1.0 milestone*
