# Stack Research

**Project:** ErrorMux v1.1 Polish & Package
**Milestone:** Subsequent — Adding fixes and improvements to existing zsh plugin
**Researched:** 2026-04-16
**Confidence:** HIGH

---

## Executive Summary

This is a **subsequent milestone** for an existing, validated zsh plugin. No new core Python dependencies are needed. The changes are primarily:

1. **Pure zsh fix** for widget auto-return (no dependencies)
2. **Configuration change** to switch model name (no library changes)
3. **Packaging structure** for Oh My Zsh compatibility (directory conventions)
4. **Repo polish** using standard tools (GitHub Actions, shields.io, VHS)

---

## Existing Stack (Validated, No Changes Needed)

| Technology | Version | Purpose | Status |
|------------|---------|---------|--------|
| Python | 3.12+ | Runtime | ✓ Unchanged |
| uv | 0.5+ | Package manager | ✓ Unchanged |
| ollama SDK | 0.6.1+ | Ollama Python SDK | ✓ Unchanged |
| typer | 0.15+ | CLI framework | ✓ Unchanged |
| rich | 14.0+ | Terminal output | ✓ Unchanged |
| SQLite | (stdlib) | Cache storage | ✓ Unchanged |
| pytest | 8.0+ | Testing | ✓ Unchanged |
| pytest-cov | 5.0+ | Coverage reporting | ✓ Unchanged |

**Current test coverage:** 92% (63 tests passing)

---

## NEW: Stack Additions for v1.1

### 1. Widget Exit Fix (Pure Zsh)

**No dependencies needed.** This is a zle (zsh line editor) fix using built-in commands.

| Component | Purpose | Notes |
|-----------|---------|-------|
| `zle reset-prompt` | Redraw prompt after widget | Built-in zsh command |
| `zle accept-line` | Accept empty line (optional) | Built-in zsh command |

**Fix Pattern:**
```zsh
_errormux_explain() {
    # ... existing logic ...
    errormux
    zle reset-prompt  # Add this line - redraws prompt after output
}
```

### 2. Model Switch: gemma3:4b → gemma4:e2b

**No library changes needed.** Just update the constant in `client.py`.

| Aspect | Before (gemma3:4b) | After (gemma4:e2b) |
|--------|--------------------|--------------------|
| Model size | ~4GB | 7.2GB |
| Context window | 8K tokens | 128K tokens |
| Modalities | Text | Text, Image, Audio |
| Benchmark (LiveCodeBench v6) | 29.1% | 44.0% |

**Change Required:**
```python
# In src/errormux/client.py, line 10
OLLAMA_MODEL = "gemma4:e2b"  # Changed from gemma3:4b
```

**Verification:** gemma4:e2b confirmed available at ollama.com/library/gemma4 (HIGH confidence, verified 2026-04-16)

### 3. Demo GIF Recording

| Tool | Version | Purpose | When to Use |
|------|---------|---------|-------------|
| **VHS** | 0.11.0+ | Terminal GIF recording | Primary choice for demos |
| asciinema | 2.x | Terminal recording (web embed) | Alternative if no GIF needed |

**VHS Installation:**
```bash
# macOS
brew install vhs

# Requires dependencies
brew install ttyd ffmpeg
```

**VHS tape file pattern:**
```tape
# demo.tape
Output demo.gif
Set FontSize 18
Set Width 800
Set Height 400
Set Shell "zsh"

Type "ls /nonexistent"
Enter
Sleep 1s
Type "??"
Sleep 2s
```

### 4. GitHub Actions CI

| Action | Version | Purpose |
|--------|---------|---------|
| `actions/checkout` | v6 | Clone repository |
| `actions/setup-python` | v6 | Install Python |
| `astral-sh/setup-uv` | v5 | Install uv package manager |

**Workflow file (`.github/workflows/ci.yml`):**
```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: '3.12'
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --group dev
      - run: uv run pytest
```

### 5. README Badges

| Badge | Source | URL Pattern |
|-------|--------|-------------|
| Test status | GitHub Actions | `https://github.com/{owner}/{repo}/actions/workflows/ci.yml/badge.svg` |
| Coverage | shields.io (static) | `https://img.shields.io/badge/coverage-92%25-green` |
| License | shields.io | `https://img.shields.io/badge/license-MIT-blue.svg` |
| Python version | shields.io | `https://img.shields.io/badge/python-3.12+-blue.svg` |

**Badge Markdown:**
```markdown
[![Tests](https://github.com/kartikparsoya-eng/ErrorMux/actions/workflows/ci.yml/badge.svg)](https://github.com/kartikparsoya-eng/ErrorMux/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/coverage-92%25-green)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
```

### 6. LICENSE File

| License | Why | Notes |
|---------|-----|-------|
| **MIT** | Most permissive, widely used, matches typical CLI tools | Standard for open source developer tools |

**No dependencies** — just create `LICENSE` file with MIT text.

---

## Oh My Zsh Plugin Structure

| File | Purpose | Required |
|------|---------|----------|
| `errormux.plugin.zsh` | Main plugin file | ✓ Required |
| `_errormux` | Completion definitions | Optional |
| `README.md` | Plugin documentation | Recommended |

**Oh My Zsh installation pattern:**
```bash
# User clones to custom plugins directory
git clone https://github.com/kartikparsoya-eng/ErrorMux.git \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/errormux

# User adds to .zshrc plugins array
plugins=(... errormux)
```

**Current file already named correctly:** `errormux.plugin.zsh` ✓

---

## What NOT to Add

| Avoid | Why | Instead |
|-------|-----|---------|
| `requests` library | Already using httpx via ollama SDK | Keep ollama SDK |
| New Python dependencies | Increases install complexity, contradicts "minimal" constraint | Stay minimal |
| Complex CI matrix (multiple OS/Python) | Overkill for single-user local plugin | Simple `uv run pytest` |
| Homebrew formula | Premature for v1.1, adds maintenance burden | Manual/git install for now |
| PyPI package | This is a zsh plugin, not a Python library | Keep as source install |
| codecov.io integration | Overkill for small project | Use shields.io static badge with current 92% |

---

## Installation Commands

### For Development (existing, unchanged)
```bash
uv sync --group dev
uv run pytest
```

### For VHS (demo recording)
```bash
brew install vhs ttyd ffmpeg
vhs demo.tape
```

### For Oh My Zsh users (new)
```bash
git clone https://github.com/kartikparsoya-eng/ErrorMux.git \
  ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/errormux
# Add 'errormux' to plugins array in ~/.zshrc, then restart shell
```

### For manual install (existing, unchanged)
```bash
git clone https://github.com/kartikparsoya-eng/ErrorMux.git
cd ErrorMux
./install.sh
```

---

## Version Compatibility

| Component A | Compatible With | Notes |
|-------------|-----------------|-------|
| gemma4:e2b | ollama SDK 0.6.1+ | Same API, just model name change |
| setup-python@v6 | GitHub Actions runner v2.327.1+ | Node 24 based |
| VHS 0.11+ | macOS 12+, Linux | Requires ttyd + ffmpeg |
| uv 0.5+ | Python 3.12+ | Already in use |
| typer 0.15+ | rich 14.0+ | Already in use |

---

## Integration Points

### Widget → CLI (unchanged)
- Widget calls `errormux` CLI command
- CLI reads `/tmp/shell-explainer-*` files
- CLI calls Ollama, displays output via Rich

### Widget Auto-Return (NEW - pure zsh)
- Add `zle reset-prompt` at end of `_errormux_explain()` function
- No changes to CLI or Python code required
- This redraws the prompt immediately after output

### Model Switch (NEW - config only)
- Single line change in `src/errormux/client.py`: `OLLAMA_MODEL = "gemma4:e2b"`
- All existing tests still pass (model name is not part of test contracts)
- User must run `ollama pull gemma4:e2b` before first use

---

## Alternatives Considered for Demo Recording

| Tool | Pros | Cons | Decision |
|------|------|------|----------|
| **VHS** | Declarative `.tape` files, reproducible, CI-friendly | Requires ttyd + ffmpeg | ✓ Recommended |
| asciinema | Simple recording, web embeds | No GIF output, requires asciinema.org account | Alternative |
| terminalizer | Node-based, configurable GIF output | Slower, requires Node.js | Not recommended |
| ttygif | Direct terminal → GIF | Manual recording, no scripting | Not recommended |

---

## Sources

- [ollama.com/library/gemma4](https://ollama.com/library/gemma4) — gemma4:e2b model details (HIGH confidence, verified 2026-04-16)
- [github.com/charmbracelet/vhs](https://github.com/charmbracelet/vhs) — Terminal GIF recorder (HIGH confidence)
- [github.com/actions/setup-python](https://github.com/actions/setup-python) — CI action v6 (HIGH confidence)
- [github.com/ohmyzsh/ohmyzsh/wiki/Plugins](https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins) — Plugin structure (HIGH confidence)
- [shields.io](https://shields.io) — Badge service (HIGH confidence)
- [Oh My Zsh git.plugin.zsh](https://github.com/ohmyzsh/ohmyzsh/blob/master/plugins/git/git.plugin.zsh) — Plugin file structure example (HIGH confidence)

---

## Summary: No New Python Dependencies Required

The v1.1 milestone is purely about:
1. **Fixing zsh behavior** — built-in `zle reset-prompt`
2. **Changing config** — update model name constant
3. **Packaging structure** — already correct file naming
4. **Repo polish** — GitHub Actions (not a Python dep), shields.io (external service), VHS (dev tool only)

The stack remains minimal: Python 3.12, uv, ollama SDK, typer, rich, SQLite — exactly as validated in v1.0.

---

*Stack research for: ErrorMux v1.1 Polish & Package*
*Researched: 2026-04-16*
