# Milestones

## v1.1 Polish & Package (Shipped: 2026-04-16)

**Phases completed:** 4 phases, 11 plans

**Key accomplishments:**

- Added ZLE reset pattern (`zle reset-prompt` + `zle -R`) for automatic prompt return after `??` output
- Updated model to gemma4:e2b with model-scoped cache keys to prevent stale explanations
- Config file at ~/.shell-explainer/config.toml documents model requirement with helpful error messages
- Multi-method installation support: Oh My Zsh, one-line curl, and manual git clone
- Comprehensive README with install docs, update procedures, and uninstall instructions
- Published to GitHub with MIT license, shields.io badges, and formal v1.1.0 release

---

## v1.0 MVP (Shipped: 2026-04-16)

**Phases completed:** 6 phases, 12 plans, 20 tasks

**Key accomplishments:**

- Zsh plugin with preexec/precmd hooks capturing command context (text, stderr, exit code) and `??` widget triggering Python CLI
- Python CLI with Ollama integration, streaming Rich output, 10s timeout, and graceful offline handling
- SQLite cache with 7-day TTL for instant explanations on repeated errors
- Skip-list filtering for false-positive errors (grep exit 1, test/[[, diff exit 1)
- Single-command installer that clones repo, modifies .zshrc, and installs Python deps via uv
- pytest-cov test suite with 92% coverage using httpx MockTransport

---
