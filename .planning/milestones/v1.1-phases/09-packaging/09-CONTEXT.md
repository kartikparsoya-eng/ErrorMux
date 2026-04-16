# Phase 9: Packaging - Context

**Gathered:** 2026-04-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Provide multiple documented installation methods for public distribution: Oh My Zsh plugin, one-line curl install, and manual git clone + .zshrc edit. Users should be able to install, update, and uninstall cleanly.

This phase does NOT change the plugin functionality, keybinding, or CLI behavior. It focuses purely on packaging and documentation.

</domain>

<decisions>
## Implementation Decisions

### Oh My Zsh Detection

- **D-01:** Check `$ZSH_CUSTOM` environment variable first (primary detection)
- **D-02:** Fallback to `~/.oh-my-zsh/custom/plugins` if `$ZSH_CUSTOM` not set
- **D-03:** If neither found, use `~/.shell-explainer` as fallback path
- **Rationale:** Covers custom ZSH locations via env var, standard Oh My Zsh installs via default path, and non-Oh My Zsh users via consistent fallback.

### Install Path Strategy

- **D-04:** Detect Oh My Zsh and use `$ZSH_CUSTOM/plugins/errormux/` (or fallback path) if found
- **D-05:** Otherwise use `~/.shell-explainer/` (existing default)
- **D-06:** Single install script handles both cases automatically
- **Rationale:** Oh My Zsh users get standard plugin path experience. Non-Oh My Zsh users get consistent single-location install.

### Oh My Zsh Activation

- **D-07:** Print clear instructions for adding `errormux` to plugins array
- **D-08:** Do NOT auto-modify `.zshrc` `plugins=(...)` array
- **D-09:** Show instruction: `Add 'errormux' to your plugins array in ~/.zshrc`
- **Rationale:** Auto-modifying the plugins array is risky (complex parsing, potential to break shell config). Manual edit is safer and Oh My Zsh users expect this pattern.

### Update Experience

- **D-10:** Re-running `install.sh` detects existing installation and updates in-place
- **D-11:** Existing `git pull` logic in install.sh handles updates
- **D-12:** Document update method in README: "To update, re-run the install command"
- **Rationale:** Single script serves both install and update. Keeps maintenance simple.

### Uninstall Support

- **D-13:** Provide `uninstall.sh` script in repo root
- **D-14:** Script removes plugin directory (detected from install location)
- **D-15:** Script prints instructions for `.zshrc` cleanup (remove source line or plugins entry)
- **D-16:** Do NOT auto-modify `.zshrc` during uninstall
- **Rationale:** Clean removal without risking .zshrc corruption. User handles final cleanup step.

### Documentation Requirements

- **D-17:** README documents three install methods:
  1. Oh My Zsh (clone to `$ZSH_CUSTOM/plugins/errormux/`)
  2. One-line curl (install.sh)
  3. Manual (git clone + .zshrc edit)
- **D-18:** README documents update and uninstall procedures
- **D-19:** Update GitHub repo URL in install.sh from placeholder to actual URL

### Claude's Discretion

- Exact wording of installation instructions
- Formatting of success/error messages
- Whether to add color output to uninstall.sh

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Install Script
- `install.sh` — Current installer, needs Oh My Zsh detection added
- `install.sh:15-20` — Current path constants (hardcoded)
- `install.sh:50-65` — Clone/update logic

### Plugin File
- `errormux.plugin.zsh` — Plugin entry point, naming convention already correct for Oh My Zsh

### Requirements
- `.planning/REQUIREMENTS.md` — PKG-01 through PKG-05 acceptance criteria

### Prior Context
- `.planning/phases/8-model-switch/08-CONTEXT.md` — Config/cache location at `~/.shell-explainer/`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `install.sh` — Existing script handles git clone, uv sync, .zshrc modification
- `errormux.plugin.zsh` — Plugin file naming already follows Oh My Zsh convention
- `.zshrc` source line pattern — `source ~/.shell-explainer/errormux.plugin.zsh`

### Established Patterns
- Pre-flight checks before installation (uv, git)
- Colored output via ANSI escape codes
- `grep -qF` for checking .zshrc content (exact match, no regex issues)

### Integration Points
- install.sh line 6: `INSTALL_DIR="$HOME/.shell-explainer"` — needs detection logic before this
- install.sh line 9: `REPO_URL` — needs actual GitHub URL
- .zshrc modification — needs to handle Oh My Zsh plugins array instruction differently

</code_context>

<specifics>
## Specific Ideas

- Install message should feel like standard zsh plugin tooling
- Error messages should guide users to correct action
- Uninstall should be reversible (user can reinstall easily)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 09-packaging*
*Context gathered: 2026-04-16*
