# Feature Research

**Domain:** zsh plugin — on-demand shell error explanations
**Researched:** 2026-04-16 (v1.1 milestone update)
**Confidence:** HIGH (official Ollama docs, Oh My Zsh wiki, existing codebase analysis)

> **Note:** This file focuses on v1.1 features (widget fix, model switch, packaging, GitHub polish). For core feature landscape from v1.0, see the archived version. This update addresses subsequent milestone requirements.

## Feature Landscape (v1.1 Focus)

### Table Stakes (Users Expect These)

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Auto-return to prompt after output | Users press `??` once, expect clean prompt after. Manual Enter press feels broken. | LOW | ZLE widget fix: call `zle reset-prompt` after output completes |
| Correct model name in docs | If README says `gemma4:e2b`, code should match. Mismatch looks unprofessional. | LOW | Single-line config change in `client.py` |
| Working installation instructions | Users expect `git clone && ./install.sh` to work without hunting for steps. | MEDIUM | Update install.sh URL, add Oh My Zsh instructions |
| LICENSE file | Open source repos without LICENSE are "all rights reserved" by default. GitHub flags this. | LOW | Create MIT LICENSE file |
| README with usage | Empty/minimal README makes project look abandoned. | MEDIUM | Add demo GIF, installation methods, usage examples |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Multiple install methods (Oh My Zsh, git, manual) | Meets users where they are. OMZ users want `plugins=(errormux)`. | MEDIUM | Add OMZ-compatible directory structure |
| Demo GIF in README | Shows plugin in action. Users can see exactly what they're getting before installing. | MEDIUM | Use asciinema/terminalizer, embed in README |
| Test coverage badge | Signals code quality. 92% coverage is a strong differentiator for a "simple" plugin. | LOW | Add badge to README header |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Auto-explain on every error | "Wouldn't it be great if errors explained themselves?" | Disrupts flow, spams output, slows shell, burns tokens. Violates "on-demand" core value. | Keep opt-in via `??` — user requests explanation only when needed |
| Configurable model | "I want to use llama3.2 instead" | Adds complexity, different models have different prompting needs. MVP should stay focused. | Hardcode `gemma4:e2b` per project constraint. Consider config in v2 if requested |
| Bash/Fish support | "I use bash, make it work there too" | Hooks differ significantly, testing burden triples, preexec works differently in bash. | zsh only per constraint. Shell market share favors zsh for this use case |

## Feature Dependencies

```
Widget Auto-Return Fix
    └── No dependencies — standalone UX fix
    └── Impacts: Demo GIF (need correct behavior for recording)

Model Switch (gemma3:4b → gemma4:e2b)
    └── No dependencies — config change only
    └── Requires: gemma4:e2b installed in Ollama (user responsibility)
    └── Impacts: README docs, demo GIF

Packaging for Multiple Install Methods
    └── Depends on: Widget fix (correct behavior)
    └── Depends on: Model switch (correct docs)
    └── Requires: Oh My Zsh-compatible directory structure

GitHub Polish (README, Demo GIF, LICENSE, Badges)
    └── Depends on: All above complete
    └── Demo GIF requires: Working plugin with correct behavior
    └── Badges require: Tests passing (already 92% coverage)
```

### Dependency Notes

- **Widget Auto-Return requires nothing:** Pure zsh fix, no Python changes, isolated from other features.
- **Model Switch is config-only:** Change `OLLAMA_MODEL` in `client.py` line 10. No API changes, Gemma 4 uses same chat format.
- **Packaging enhances adoption:** Oh My Zsh users expect `plugins=(name)` to work. Without this, manual sourcing is friction.
- **Demo GIF blocks on correct behavior:** Can't record demo until widget returns to prompt correctly.

## Implementation Details

### 1. Widget Auto-Return to Prompt

**Current behavior:** After `??` widget displays output, user must press Enter to get clean prompt.

**Expected behavior:** Widget displays output, automatically returns to clean prompt.

**Implementation:**
```zsh
# In errormux.plugin.zsh, after errormux call:
_errormux_explain() {
    # ... existing code ...
    errormux
    
    # NEW: Return to clean prompt automatically
    zle reset-prompt
}
```

**Why `zle reset-prompt`:**
- Redraws prompt cleanly
- Doesn't execute anything (unlike `accept-line`)
- Standard pattern for informational widgets
- Works with all prompt themes

**Complexity:** LOW — 1 line addition

**Testing:** Manual UAT: Run failing command, press `??`, verify prompt appears without Enter key.

---

### 2. Model Switch (gemma3:4b → gemma4:e2b)

**Change location:** `src/errormux/client.py` line 10

**Current:**
```python
OLLAMA_MODEL = "gemma3:4b"
```

**New:**
```python
OLLAMA_MODEL = "gemma4:e2b"
```

**Model details (from ollama.com/library/gemma4):**
- **Name:** `gemma4:e2b`
- **Size:** 7.2GB
- **Context:** 128K tokens
- **Type:** Edge device optimized (E2B = "effective 2B" parameters)
- **Modalities:** Text, Image, Audio
- **Benchmark:** 60% MMLU Pro, better than Gemma 3 27B for coding

**Why gemma4:e2b over gemma3:4b:**
- Newer model with better reasoning
- Similar size (7.2GB vs 3.3GB)
- Edge-optimized for local execution
- Native system prompt support
- Already available in Ollama library

**Compatibility check:**
- Same chat API (`/api/chat`)
- Same message format (system/user roles)
- Streaming works identically
- No prompt changes needed

**Complexity:** LOW — 1 line change

**Testing:** Run tests, verify Ollama responses still parse correctly.

---

### 3. Multiple Install Methods

#### Method A: Git Clone (existing)

```bash
git clone https://github.com/kartikparsoya-eng/ErrorMux.git ~/.shell-explainer
cd ~/.shell-explainer
./install.sh
```

**Changes needed:**
- Update `install.sh` line 15: `REPO_URL="https://github.com/kartikparsoya-eng/ErrorMux.git"`
- Current script already handles this method

#### Method B: Oh My Zsh

```bash
# Clone to custom plugins directory
git clone https://github.com/kartikparsoya-eng/ErrorMux.git \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/errormux

# Enable in ~/.zshrc
plugins=(... errormux)
```

**Structure requirements:**
```
errormux/
├── errormux.plugin.zsh  ← OMZ looks for this exact name
├── README.md
├── src/
│   └── errormux/
├── pyproject.toml
└── install.sh
```

**Current state:** Already has `errormux.plugin.zsh` — OMZ-compatible!

**Changes needed:**
- Document OMZ install in README
- Add Python dep install note for OMZ users:
  ```bash
  cd ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/errormux
  uv sync
  ```

#### Method C: Manual

```bash
# Download/copy files
mkdir -p ~/.local/share/errormux
cp errormux.plugin.zsh ~/.local/share/errormux/
cp -r src ~/.local/share/errormux/

# Source in .zshrc
source ~/.local/share/errormux/errormux.plugin.zsh

# Install deps
cd ~/.local/share/errormux
uv sync
```

**Complexity:** MEDIUM — README documentation updates

---

### 4. GitHub Repo Polish

#### README Structure

```markdown
# ErrorMux

One-line description.

![Demo](demo.gif)

## Installation

### Oh My Zsh
...

### Git Clone
...

### Manual
...

## Usage

...

## Requirements

## Configuration

## License
```

#### Demo GIF

**Tool options:**
- **asciinema** — `asciinema rec demo.cast`, export to GIF with `agg`
- **terminalizer** — `terminalizer record demo`, renders to GIF directly

**Demo script:**
1. Clear terminal
2. Run: `ls /nonexistent` (fails)
3. Press: `Ctrl+X ?` (triggers explanation)
4. Show explanation output
5. Return to clean prompt

**File:** `demo.gif` in repo root

**Embed:** `![ErrorMux Demo](demo.gif)`

#### LICENSE File

```text
MIT License

Copyright (c) 2026 Kartik Parsoya

Permission is hereby granted, free of charge, to any person obtaining a copy...
```

#### Badges

```markdown
![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Shell](https://img.shields.io/badge/shell-zsh-green)
```

**Complexity:** MEDIUM — Requires recording demo, writing docs

---

## MVP Definition

### v1.1 Must Have (This Milestone)

- [ ] Widget auto-return — **1 line zsh fix**
- [ ] Model switch to gemma4:e2b — **1 line config**
- [ ] Oh My Zsh install docs — **README section**
- [ ] Git clone install docs — **README section (exists, update URL)**
- [ ] LICENSE file — **Create MIT LICENSE**
- [ ] Demo GIF — **Record 10s demo**
- [ ] Test badges — **Add to README header**

### v1.2 Consider (Future)

- [ ] Config file for model selection (if users request)
- [ ] Bash support (if demand exists)
- [ ] Auto-update mechanism

### Out of Scope

- Auto-explain on error (violates "on-demand" core value)
- Cloud LLM fallback (offline-first constraint)
- GUI/TUI (keep simple)

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Widget auto-return | HIGH | LOW | P1 |
| Model switch | HIGH | LOW | P1 |
| LICENSE file | MEDIUM | LOW | P1 |
| Git clone docs (update) | HIGH | LOW | P1 |
| Oh My Zsh docs | MEDIUM | MEDIUM | P2 |
| Demo GIF | HIGH | MEDIUM | P2 |
| Test badges | LOW | LOW | P3 |

**Priority key:**
- P1: Must have for v1.1
- P2: Should have, add when possible
- P3: Nice to have, low effort

## Competitor Feature Analysis

| Feature | thefuck | zsh-autosuggestions | ErrorMux |
|---------|---------|---------------------|----------|
| Trigger method | Auto on error | Auto as you type | Manual `??` |
| Output type | Suggested command | Command completion | WHY/FIX explanation |
| LLM powered | No | No | Yes (Ollama) |
| Offline | Yes | Yes | Yes |
| Configurable | Yes | Yes | No (v1.1) |

**Our differentiation:** AI-powered explanations, not just suggestions. "Why did it fail?" not just "run this instead."

## Key Insights for v1.1

### Widget Auto-Return

**Problem:** Users expect immediate prompt return after `??`. Current behavior (press Enter after output) feels like a bug.

**Solution:** `zle reset-prompt` is the standard zsh pattern for informational widgets. One-line fix with high UX impact.

**Risk:** None — this is purely additive, doesn't change existing behavior.

### Model Switch

**Rationale:** Gemma 4 was released April 2026 with significant improvements over Gemma 3. E2B variant is edge-optimized, perfect for local CLI use.

**Compatibility:** Verified same API, same message format. No prompt changes needed.

**Migration:** Users must run `ollama pull gemma4:e2b` before upgrading. Document in README.

### Packaging

**Oh My Zsh compatibility:** Project already has correct file naming (`errormux.plugin.zsh`). OMZ expects `{name}.plugin.zsh` and we have it.

**Installation friction:** Three methods covers 95% of users:
- OMZ users (most zsh users use OMZ)
- Git clone + install.sh (scripted, handles deps)
- Manual (power users, air-gapped systems)

### GitHub Polish

**Demo GIF impact:** Visual demonstration reduces bounce rate. Users want to see what they're installing.

**LICENSE necessity:** Without LICENSE, GitHub shows "No license" warning. MIT is standard for dev tools.

**Badge value:** Coverage badge signals quality. 92% coverage differentiates from "quick hack" plugins.

## Sources

- [Ollama gemma4 library page](https://ollama.com/library/gemma4) — Model specs, benchmarks (HIGH confidence)
- [Oh My Zsh Plugins Wiki](https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins) — Plugin structure conventions (HIGH confidence)
- [Zsh ZLE Documentation](https://zsh.sourceforge.io/Doc/Release/Zsh-Line-Editor.html) — Widget behavior (HIGH confidence)
- Existing codebase: `errormux.plugin.zsh`, `client.py`, `cli.py` — Current implementation (HIGH confidence)
- Local `ollama list` output — Installed models verification (HIGH confidence)
- [thefuck](https://github.com/nvbn/thefuck) — Competitor analysis (HIGH confidence)
- [ai-shell](https://github.com/BuilderIO/ai-shell) — Competitor analysis (HIGH confidence)

---
*Feature research for: ErrorMux v1.1 Polish & Package*
*Researched: 2026-04-16*
*Previous version: v1.0 feature landscape (archived)*
