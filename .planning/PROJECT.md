# ErrorMux

## What This Is

A zsh plugin that explains shell command failures on-demand. When a command fails, pressing `Ctrl+X ?` triggers a local Gemma model (via Ollama) to provide a one-sentence explanation and a suggested fix. Cache-backed for speed, offline-first, zero cloud dependency.

## Core Value

Fast, local, on-demand error explanations that don't interrupt your flow — only when you ask for them.

## Requirements

### Validated

- ✓ zsh capture layer hooks stderr, exit code, and command text — v1.0
- ✓ `??` widget reads captured data and invokes Python CLI — v1.0
- ✓ Python CLI checks SQLite cache (7-day TTL) before calling Ollama — v1.0
- ✓ Ollama returns structured WHY/FIX output, streamed via Rich — v1.0
- ✓ Skip-list filters false-positive "errors" (grep exit 1, test/[[, diff exit 1) — v1.0
- ✓ Install script sets up plugin, Python deps, and .zshrc sourcing — v1.0
- ✓ Test suite covers cache, skip-list, and prompt construction — v1.0 (92% coverage)
- ✓ Widget auto-returns to prompt after showing output — v1.1
- ✓ Model switched to gemma4:e2b with model-scoped cache keys — v1.1
- ✓ Config file documents model requirement for users — v1.1
- ✓ Multi-method installation (Oh My Zsh, curl, manual) — v1.1
- ✓ Comprehensive README with install/uninstall docs — v1.1
- ✓ MIT License and GitHub badges — v1.1
- ✓ Published to github.com/kartikparsoya-eng/ErrorMux — v1.1

### Active

(None — milestone complete)

### Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-printing on every error | Opt-in via `??` only is core value |
| Cloud fallback or remote LLM APIs | Offline-first is core value |
| Multi-shell support (bash/fish) | zsh-specific hooks are core to design |
| GUI or TUI | Single ?? output is core design |
| GitHub Actions CI workflow | Deferred to v2 (requires repo setup first) |

## Context

- **Shipped:** v1.0 MVP (2026-04-16), v1.1 Polish & Package (2026-04-16)
- **LOC:** 1,370 lines Python
- **Test coverage:** 89% (64 tests passing)
- Ollama runs locally at localhost:11434 with gemma4:e2b
- Python 3.12 with `uv` for dependency management (httpx, typer, rich, tomli)
- zsh plugin uses preexec/precmd hooks for capture
- Cache stored at `~/.shell-explainer/cache.db`
- Config at `~/.shell-explainer/config.toml`
- **GitHub:** https://github.com/kartikparsoya-eng/ErrorMux

## Constraints

- **Stack**: Python 3.12, uv, httpx, typer, rich, SQLite — minimal dependencies
- **Model**: gemma4:e2b via Ollama localhost:11434 (hard requirement)
- **Timeout**: 10s max for Ollama requests; graceful degradation on failure
- **Shell**: zsh only — leverages zsh-specific hook mechanisms

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Cache TTL: 7 days | Balances staleness risk with cache utility | ✓ Good |
| Concurrency: Block on in-flight request | Simplest implementation, avoids race conditions | ✓ Good |
| Plugin name: errormux | Matches directory name, shorter than shell-explainer | ✓ Good |
| SQLite for cache | Local, zero-config, fast lookups by SHA256 key | ✓ Good |
| httpx MockTransport for testing | Strict TEST-04 compliance, tests real transport layer | ✓ Good (89% achieved) |
| pytest-cov 80% threshold | Industry standard, catches uncovered paths | ✓ Good |
| Ctrl+X ? binding | Avoids zsh glob conflicts with ?? | ✓ Good |
| ZLE reset pattern for widget | Standard zsh pattern for clean prompt return | ✓ Good |
| Model name in cache key | Prevents stale explanations after model switch | ✓ Good |
| Config file auto-generation | Users know what model to install | ✓ Good |
| Multi-method installation | Reaches wider audience (Oh My Zsh users) | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**v1.1 Changes:**
- All Active requirements moved to Validated
- Context updated with v1.1 release info
- 4 new Key Decisions added from v1.1 phases

---

*Last updated: 2026-04-16 after v1.1 milestone completion*
