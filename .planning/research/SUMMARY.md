# Project Research Summary

**Project:** ErrorMux v1.1 Polish & Package
**Domain:** zsh plugin — on-demand shell error explanations via local LLM
**Researched:** 2026-04-16
**Confidence:** HIGH

## Executive Summary

ErrorMux is an existing, validated zsh plugin that explains shell command failures on-demand using a local Gemma model via Ollama. This v1.1 milestone focuses on polish and packaging: fixing a widget exit behavior that leaves users pressing Enter after explanations, switching to the newer gemma4:e2b model, supporting Oh My Zsh installation, and polishing the GitHub repository with documentation, badges, and a demo GIF.

The recommended approach is straightforward: the widget auto-return fix is a single `zle reset-prompt` line in pure zsh; the model switch is a one-line constant change; Oh My Zsh compatibility is already satisfied by correct file naming (`errormux.plugin.zsh`); and GitHub polish uses standard tools (GitHub Actions, shields.io, VHS for demo recording). No new Python dependencies are needed — the existing minimal stack (Python 3.12, uv, ollama SDK, typer, rich, SQLite) remains unchanged.

Key risks are minimal: the widget fix has a standard zsh pattern with high confidence; the model switch requires users to pull gemma4:e2b first (document in README); cache keys should include model name to avoid stale explanations. The existing 92% test coverage provides strong validation foundation.

## Key Findings

### Recommended Stack

**No new dependencies required.** This is a subsequent milestone for an existing plugin with a validated stack. Changes are:
1. Pure zsh fix (built-in `zle reset-prompt`)
2. Config change (model name constant)
3. Packaging structure (directory conventions only)
4. Repo polish (GitHub Actions, shields.io, VHS — dev tools, not Python deps)

**Existing stack (unchanged):**
- **Python 3.12+**: Runtime — modern async support, performance
- **uv**: Package manager — 10-100x faster than pip, single tool for deps
- **ollama SDK 0.6.1+**: Ollama client — official Python SDK, handles streaming and errors
- **typer 0.15+**: CLI framework — auto help generation, Rich integration
- **rich 14.0+**: Terminal output — beautiful formatting, integrated with typer
- **SQLite**: Cache storage — zero-config, single-file, fast key-value

**Dev tools for v1.1:**
- **VHS**: Terminal GIF recording for demo
- **GitHub Actions**: CI for test badge
- **shields.io**: Static badges (coverage, license)

### Expected Features

**Must have (table stakes for v1.1):**
- **Auto-return to prompt** — users expect one keystroke, not Enter after output
- **Correct model name (gemma4:e2b)** — README and code must match
- **Working installation instructions** — git clone + install.sh, Oh My Zsh method
- **LICENSE file** — GitHub flags repos without LICENSE as "all rights reserved"
- **README with usage** — empty README looks abandoned

**Should have (differentiators):**
- **Multiple install methods** — Oh My Zsh, git clone, manual — meets users where they are
- **Demo GIF** — shows plugin in action before installing
- **Test coverage badge** — 92% coverage signals quality

**Defer (v2+):**
- **Configurable model** — adds complexity, MVP should stay focused on gemma4:e2b
- **Bash/Fish support** — hooks differ significantly, testing burden triples
- **Auto-explain on error** — violates "on-demand" core value

### Architecture Approach

The existing architecture remains unchanged. Widget hooks (preexec/precmd) capture command state, store in /tmp files. The `??` zle widget calls Python CLI which checks cache, calls Ollama, displays output. The fix adds `zle reset-prompt` after CLI output to restore prompt state.

**Major components:**
1. **errormux.plugin.zsh** — zsh hooks (preexec/precmd), zle widget binding, state capture
2. **cli.py** — typer CLI entry point, orchestrates flow
3. **client.py** — Ollama client, contains `OLLAMA_MODEL` constant (change to gemma4:e2b)
4. **cache.py** — SQLite cache with 7-day TTL

**Data flow (after fix):**
```
Command fails → precmd captures exit/stderr → User presses ??
→ Widget reads /tmp files → Calls Python CLI → Ollama explains
→ zle reset-prompt (NEW) → Prompt restored cleanly
```

### Critical Pitfalls

1. **Widget doesn't return to prompt** — Add `zle reset-prompt` AND `zle -R` after Python CLI call. Standard zsh pattern for informational widgets.

2. **Model name mismatch** — Centralize model name in one constant (`OLLAMA_MODEL` in client.py). Document `ollama pull gemma4:e2b` in README. Verify model available at startup.

3. **Cache keys invalid after model switch** — Include model name in cache key, or use version prefix (`CACHE_VERSION = "v2-gemma4"`). Prevents stale explanations from gemma3:4b.

4. **Oh My Zsh installation path wrong** — Install to `$ZSH_CUSTOM/plugins/errormux/` (NOT `$ZSH/plugins/`). File MUST be named `errormux.plugin.zsh` (already correct).

5. **Demo GIF doesn't capture keybinding** — Use VHS (declarative .tape files) or asciinema + agg. Show `Ctrl+X ?` triggering explanation clearly.

## Implications for Roadmap

Based on research, suggested phase structure for v1.1:

### Phase 1: Widget Auto-Return Fix
**Rationale:** Simplest change, no dependencies, high UX impact. Should be done first because demo GIF requires correct behavior.
**Delivers:** Clean prompt return after `??` widget
**Addresses:** Table stake: auto-return to prompt
**Avoids:** Pitfall — widget doesn't return to prompt
**Changes:** Add 2 lines to `errormux.plugin.zsh`

### Phase 2: Model Switch
**Rationale:** One-line config change, but impacts README docs. Cache key consideration.
**Delivers:** Uses gemma4:e2b model (better reasoning, 128K context)
**Addresses:** Table stake: correct model name in docs
**Avoids:** Pitfall — model name mismatch, cache key invalid
**Changes:** `client.py` line 10, cache key logic, README requirements

### Phase 3: Packaging (Oh My Zsh + Install Docs)
**Rationale:** Structure is already correct, needs documentation. Multiple install methods.
**Delivers:** Oh My Zsh compatibility, clear install instructions
**Addresses:** Table stake: working installation instructions; Differentiator: multiple install methods
**Avoids:** Pitfall — Oh My Zsh installation path wrong
**Changes:** README install sections, optionally update install.sh

### Phase 4: GitHub Polish (README, LICENSE, Badges, Demo)
**Rationale:** Final touch, depends on correct behavior for demo GIF
**Delivers:** Professional GitHub presence, demo for adoption
**Addresses:** Table stake: LICENSE, README with usage; Differentiator: demo GIF, badges
**Avoids:** Pitfall — LICENSE missing, badge URLs stale, demo GIF broken
**Changes:** LICENSE file, README rewrite, GitHub Actions workflow, demo.gif

### Phase Ordering Rationale

- **Widget fix first** — Demo GIF must show correct behavior; this is the highest UX impact per line of code
- **Model switch second** — Config change is isolated; must be done before final README docs
- **Packaging third** — Documentation changes; depends on widget fix and model switch being correct
- **Polish last** — Demo GIF, badges depend on everything else being finalized

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4 (Demo GIF):** VHS tool specifics, terminal recording quirks with zsh prompts — consider `/gsd-research-phase` if issues arise

Phases with standard patterns (skip research-phase):
- **Phase 1:** Well-documented zsh ZLE pattern (`zle reset-prompt`)
- **Phase 2:** One-line constant change, no complexity
- **Phase 3:** Oh My Zsh plugin structure is well-documented

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Existing validated stack, no new deps, official Ollama docs verified |
| Features | HIGH | Clear table stakes, defined MVP scope, existing codebase |
| Architecture | HIGH | Single-line zsh fix, single-line config change, standard patterns |
| Pitfalls | HIGH | Official zsh ZLE docs, Oh My Zsh wiki, Ollama library verified |

**Overall confidence:** HIGH

### Gaps to Address

- **User must pull gemma4:e2b:** Document in README as prerequisite. Consider startup check that shows helpful error if model not found.
- **Demo GIF recording:** VHS requires ttyd + ffmpeg dependencies. May need troubleshooting on first recording. Handle during execution.

## Sources

### Primary (HIGH confidence)
- [Ollama gemma4 library](https://ollama.com/library/gemma4) — Model specs, naming conventions
- [Oh My Zsh Plugins Wiki](https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins) — Plugin structure, installation
- [Zsh ZLE Documentation](https://zsh.sourceforge.io/Doc/Release/Zsh-Line-Editor.html) — Widget behavior, reset-prompt
- [ollama-python SDK](https://github.com/ollama/ollama-python) — Official Python client, error handling
- [VHS by Charmbracelet](https://github.com/charmbracelet/vhs) — Terminal GIF recording

### Secondary (MEDIUM confidence)
- [GitHub Actions setup-python](https://github.com/actions/setup-python) — CI action versions
- [shields.io](https://shields.io) — Badge service patterns

### Tertiary (LOW confidence)
- None — all critical information verified with official sources

---
*Research completed: 2026-04-16*
*Ready for roadmap: yes*
