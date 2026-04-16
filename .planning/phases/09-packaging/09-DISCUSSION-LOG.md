# Phase 9: Packaging - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in 09-CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-16
**Phase:** 09-packaging
**Areas discussed:** Oh My Zsh Detection, Install Path Strategy, Oh My Zsh Activation, Update Experience, Uninstall Support

---

## Oh My Zsh Detection

| Option | Description | Selected |
|--------|-------------|----------|
| Check `$ZSH_CUSTOM` + fallback to `~/.oh-my-zsh/custom/plugins` | Handles custom ZSH locations, covers standard Oh My Zsh setup | ✓ |
| Check `$ZSH_CUSTOM` only | Simpler | |
| Check `~/.oh-my-zsh` directory only | Covers most installs | |
| Check all three | Maximum coverage | |

**User's choice:** Check `$ZSH_CUSTOM` first, fallback to `~/.oh-my-zsh/custom/plugins`
**Notes:** Recommended approach for robustness without over-engineering.

---

## Install Path Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Detect Oh My Zsh, fallback to `~/.shell-explainer` | Oh My Zsh users get standard path, others get consistent fallback | ✓ |
| Always use `~/.shell-explainer` | Consistent, simpler docs | |
| Let user choose with `--omz` flag | Explicit control | |
| Always use Oh My Zsh path if detected | Enforces Oh My Zsh | |

**User's choice:** Detect Oh My Zsh path if available, otherwise use `~/.shell-explainer`
**Notes:** Two install locations acceptable for better Oh My Zsh integration.

---

## Oh My Zsh Activation

| Option | Description | Selected |
|--------|-------------|----------|
| Print clear instructions, don't auto-modify | Safe, no risk of breaking .zshrc | ✓ |
| Auto-modify `plugins=(...)` array with confirmation | Convenient but risky | |
| Auto-modify without asking | Fastest UX, dangerous | |
| Use `source` line regardless | Works everywhere but not Oh My Zsh pattern | |

**User's choice:** Print clear instructions, don't auto-modify .zshrc
**Notes:** Safety-first approach. Oh My Zsh users expect manual plugin activation.

---

## Update Experience

| Option | Description | Selected |
|--------|-------------|----------|
| Re-run install.sh (detects existing, updates in-place) | Single script, already handles `git pull` | ✓ |
| Dedicated `update.sh` script | Explicit purpose | |
| `errormux-update` widget/command | Integrated into plugin | |
| Just document `git pull` in plugin dir | Simplest | |

**User's choice:** Re-run install.sh works for updates (document in README)
**Notes:** Existing script already handles update case. Keep it simple.

---

## Uninstall Support

| Option | Description | Selected |
|--------|-------------|----------|
| Simple uninstall.sh + README instructions | Clean removal, helpful for users | ✓ |
| README instructions only | No extra code | |
| Skip uninstall support | Less work | |

**User's choice:** Provide `uninstall.sh` that removes plugin dir + prints .zshrc cleanup instructions
**Notes:** Does NOT auto-modify .zshrc. User handles final cleanup step.

---

## Claude's Discretion

- Exact wording of installation instructions
- Formatting of success/error messages
- Whether to add color output to uninstall.sh

---

## Deferred Ideas

None — discussion stayed within phase scope.

---

*Phase: 09-packaging*
*Discussion log created: 2026-04-16*
