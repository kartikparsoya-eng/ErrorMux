# Phase 5: Installation - Context

**Gathered:** 2026-04-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Create a single-command installer (install.sh) that sets up ErrorMux for end users. The installer copies the zsh plugin, updates .zshrc to source it, and ensures Python dependencies are available via uv.

**In scope:** install.sh script, .zshrc modification, Python dependency setup.
**Out of scope:** Package managers (brew, apt), version management, uninstall script.

</domain>

<canonical_refs>
## Canonical References

- `.planning/ROADMAP.md` — Phase 5 goal, requirements INST-01..03
- `.planning/REQUIREMENTS.md` — INST-01..03 acceptance criteria
- `errormux.plugin.zsh` — Plugin file to be installed
- `pyproject.toml` — Python package configuration

No external ADRs/specs referenced.

</canonical_refs>

<decisions>
## Implementation Decisions

### Installation Method
- **D-01:** Use `curl -sSL https://.../install.sh | bash` pattern (standard for shell tools)
- **D-02:** Also support manual `git clone && ./install.sh` for users who prefer it
- **D-03:** install.sh is idempotent — safe to run multiple times

### Directory Convention
- **D-04:** Install plugin to `~/.shell-explainer/` (NOT ~/.config/shell-explainer/)
  - Rationale: Phase 4 already uses `~/.shell-explainer/config.toml` for user config
  - Keeps plugin and config in one place for simplicity
  - REQUIREMENTS.md path was preliminary; consistency with Phase 4 wins
- **D-05:** Plugin file: `~/.shell-explainer/errormux.plugin.zsh`

### .zshrc Modification
- **D-06:** Source line format: `source ~/.shell-explainer/errormux.plugin.zsh`
- **D-07:** Detection: grep for exact source line, append if not found
- **D-08:** No backup file — idempotent, reversible by removing the source line

### Python/uv Setup
- **D-09:** Require uv to be pre-installed (don't bootstrap it)
- **D-10:** Run `uv tool install errormux` or `uv pip install` depending on deployment model
- **D-11:** Alternative: install.sh clones repo and runs `uv sync` for local development install
- **D-12:** Claude's Discretion: Planner chooses install model (tool install vs local clone)

### Claude's Discretion
- Exact install.sh implementation details
- Error handling and user feedback messages
- Whether to install as uv tool or local project

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `errormux.plugin.zsh` — Plugin file ready to copy
- `pyproject.toml` — Defines `errormux` CLI entry point

### Established Patterns
- uv for dependency management (PROJECT.md constraint)
- `~/.shell-explainer/` for user config (Phase 4)

### Integration Points
- .zshrc needs source line for plugin activation
- uv tool install or pip install for CLI availability

</code_context>

<specifics>
## Specific Ideas

No specific requirements — standard shell tool installation patterns.

</specifics>

<deferred>
## Deferred Ideas

- Homebrew formula (future: `brew install errormux`)
- Uninstall script
- Version checking/updates
- Multi-shell support (bash, fish)

</deferred>

---

*Phase: 05-installation*
*Context gathered: 2026-04-15*
