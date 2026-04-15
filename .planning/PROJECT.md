# ErrorMux

## What This Is

A zsh plugin that explains shell command failures on-demand. When a command fails, typing `??` triggers a local Gemma model (via Ollama) to provide a one-sentence explanation and a suggested fix. Cache-backed for speed, offline-first, zero cloud dependency.

## Core Value

Fast, local, on-demand error explanations that don't interrupt your flow — only when you ask for them.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] zsh capture layer hooks stderr, exit code, and command text for every interactive command
- [ ] `??` widget reads captured data and invokes Python CLI
- [ ] Python CLI checks SQLite cache (7-day TTL) before calling Ollama
- [ ] Ollama returns structured WHY/FIX output, streamed via Rich
- [ ] Skip-list filters out false-positive "errors" (grep exit 1, test/[[, diff exit 1)
- [ ] Install script sets up plugin, Python deps, and .zshrc sourcing
- [ ] Test suite covers cache, skip-list, and prompt construction

### Out of Scope

- Auto-printing on every error (opt-in via `??` only)
- Cloud fallback or remote LLM APIs
- Multi-shell support (zsh only, no bash/fish)
- GUI or TUI beyond the single `??` output

## Context

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
| Cache TTL: 7 days | Balances staleness risk with cache utility | — Pending |
| Concurrency: Block on in-flight request | Simplest implementation, avoids race conditions | — Pending |
| Plugin name: errormux | Matches directory name, shorter than shell-explainer | — Pending |
| SQLite for cache | Local, zero-config, fast lookups by SHA256 key | — Pending |

---

*Last updated: 2026-04-15 after initialization*
