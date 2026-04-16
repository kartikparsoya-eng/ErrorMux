# Architecture Research: Widget Exit Fix, Model Switch, Packaging

**Project:** ErrorMux v1.1
**Researched:** 2026-04-16
**Mode:** Ecosystem (integration architecture)

## Executive Summary

This research covers four integration points for the existing ErrorMux zsh plugin:

1. **Widget Exit Fix**: The `??` widget needs to auto-return to prompt after showing output. Solution: use `zle reset-prompt` after Python CLI completes, then `zle -R` to redisplay.

2. **Model Switching**: Change `OLLAMA_MODEL` constant from `gemma3:4b` to `gemma4:e2b` in `client.py`. Simple one-line change, no architectural impact.

3. **Packaging**: Support three install methods:
   - Direct git clone + source (existing `install.sh`)
   - Oh My Zsh plugin (new `errormux.plugin.zsh` structure)
   - Manual installation (documented in README)

4. **GitHub Polish**: README with usage docs, demo gif, LICENSE (MIT), test badges.

## Existing Architecture

### Current Component Structure

```
ErrorMux/
├── errormux.plugin.zsh      # zsh plugin (hooks + widget)
├── src/errormux/
│   ├── cli.py               # typer CLI entry point
│   ├── client.py            # Ollama client (OLLAMA_MODEL constant)
│   ├── cache.py             # SQLite cache (~/.shell-explainer/cache.db)
│   ├── prompts.py           # System/user prompt construction
│   ├── skip.py              # Skip-list filtering
│   └── parser.py            # Response parsing
├── tests/                   # pytest suite (92% coverage)
├── pyproject.toml           # uv package config
└── install.sh               # Single-command installer
```

### Current Data Flow

```
[User types command]
        ↓
[preexec hook] → captures $3 (command text), redirects stderr
        ↓
[Command fails] → exit code != 0
        ↓
[precmd hook] → captures exit code, stderr, writes to /tmp files
        ↓
[User presses Ctrl+X ?] → zle widget invoked
        ↓
[_errormux_explain] → reads /tmp files, calls Python CLI
        ↓
[errormux CLI] → checks cache, calls Ollama, displays WHY/FIX
        ↓
[Widget returns] → prompt stays in weird state (BUG)
```

### System Overview Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interaction Layer                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Ctrl+X ?     │  │  preexec     │  │  precmd      │       │
│  │   Widget     │  │   Hook       │  │   Hook       │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
├─────────┴─────────────────┴─────────────────┴────────────────┤
│                    zsh Plugin Layer                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │          errormux.plugin.zsh                        │    │
│  │  • Hook registration (preexec_functions, precmd_functions)
│  │  • Widget binding (zle -N, bindkey)                │    │
│  │  • State capture (command, exit code, stderr)      │    │
│  │  • CLI invocation + zle reset-prompt (NEW)         │    │
│  └──────────────────────────┬──────────────────────────┘    │
│                             │                                │
├─────────────────────────────┴────────────────────────────────┤
│                   Python Backend Layer                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  cli.py      │  │  cache.py    │  │  client.py   │       │
│  │  (typer)     │  │  (SQLite)    │  │  (ollama SDK)│       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│  ┌──────┴─────────────────┴─────────────────┴───────┐       │
│  │  prompts.py, skip.py, parser.py                  │       │
│  └──────────────────────────────────────────────────┘       │
├─────────────────────────────────────────────────────────────┤
│                     External Services                        │
│  ┌──────────────────┐  ┌──────────────────────────────┐     │
│  │  Ollama API      │  │  ~/.shell-explainer/cache.db │     │
│  │  localhost:11434 │  │  ~/.shell-explainer/         │     │
│  │  gemma4:e2b      │  │                              │     │
│  └──────────────────┘  └──────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration Point 1: Widget Exit Fix

### Problem

After the widget runs, the prompt display is corrupted. Users must press Enter or type to restore normal prompt behavior.

### Root Cause

The widget function `_errormux_explain` calls an external Python process, which:
1. Invalidates the zle display (terminal output from Python)
2. Does not restore zle state after completion
3. Widget returns without refreshing the prompt

### Solution

Add `zle reset-prompt` after Python CLI completes. This forces zsh to re-expand and redisplay the prompt.

### Integration Pattern

**Modified widget function:**

```zsh
_errormux_explain() {
    local exit_code
    exit_code=$(cat /tmp/shell-explainer-last-exit 2>/dev/null || echo "0")
    
    # Skip for non-error exit codes
    if [[ "$exit_code" -eq 0 ]] || [[ "$exit_code" -eq 130 ]] || [[ "$exit_code" -eq 148 ]]; then
        return 0
    fi
    
    # Call Python CLI
    errormux
    
    # FIX: Restore prompt after external output
    zle reset-prompt
    zle -R  # Redisplay command line (clears any artifacts)
}
```

### Key ZLE Commands

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `zle reset-prompt` | Force prompt re-expansion and redisplay | After external output corrupts display |
| `zle -R` | Redisplay command line only | Lighter refresh, clears status line |
| `zle -I` | Invalidate display (prepare for output) | Before external output in traps |

### Integration Location

- **File:** `errormux.plugin.zsh`
- **Function:** `_errormux_explain`
- **Lines to modify:** Add 2 lines after line 82 (`errormux`)

### Dependencies

- None (zle built-in commands, always available in zsh)

---

## Integration Point 2: Model Switch

### Problem

Switch from `gemma3:4b` to `gemma4:e2b`.

### Current Implementation

```python
# client.py line 10
OLLAMA_MODEL = "gemma3:4b"
```

### Solution

Simple constant change:

```python
OLLAMA_MODEL = "gemma4:e2b"
```

### Configuration Options (Future)

For user-configurable models, add to `~/.shell-explainer/config.toml`:

```toml
[model]
name = "gemma4:e2b"
```

Then modify `client.py`:

```python
import tomllib
from pathlib import Path

def get_model_name() -> str:
    config_path = Path.home() / ".shell-explainer" / "config.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
            return config.get("model", {}).get("name", "gemma4:e2b")
    return "gemma4:e2b"

OLLAMA_MODEL = get_model_name()
```

### Build Order

1. **Phase 1 (this milestone):** Change constant only
2. **Future:** Add config file parsing if users request model flexibility

---

## Integration Point 3: Packaging

### Install Methods

| Method | Target User | Files Needed |
|--------|-------------|--------------|
| Git clone + source | Power users, developers | `install.sh` (existing) |
| Oh My Zsh | OMZ users | `errormux.plugin.zsh`, directory structure |
| Manual | Minimalists | README instructions |

### Oh My Zsh Plugin Structure

Oh My Zsh expects plugins in one of two locations:

```
$ZSH/plugins/errormux/           # Bundled plugins (not for 3rd party)
$ZSH_CUSTOM/plugins/errormux/    # Custom plugins (use this)
```

**Required structure:**

```
~/.oh-my-zsh/custom/plugins/errormux/
├── errormux.plugin.zsh          # Main plugin file (required naming)
├── errormux.zsh                 # Symlink or copy (optional, for completion)
├── _errormux                    # Completion definitions (optional)
├── README.md                    # Plugin documentation
└── ... (Python source, pyproject.toml, etc.)
```

### Plugin File Naming Convention

Oh My Zsh looks for `<plugin>.plugin.zsh` as the entry point. Current file `errormux.plugin.zsh` is correctly named.

### Install Script Modifications

Add Oh My Zsh detection and installation:

```bash
# install.sh additions

# Detect Oh My Zsh
if [[ -d "$HOME/.oh-my-zsh" ]]; then
    OMZ_PLUGIN_DIR="$HOME/.oh-my-zsh/custom/plugins/errormux"
    
    if [[ -d "$OMZ_PLUGIN_DIR" ]]; then
        info "Updating Oh My Zsh plugin..."
        git -C "$OMZ_PLUGIN_DIR" pull
    else
        info "Installing as Oh My Zsh plugin..."
        git clone "$REPO_URL" "$OMZ_PLUGIN_DIR"
    fi
    
    # Enable plugin in .zshrc
    if ! grep -qF "plugins=(.*errormux" ~/.zshrc; then
        sed -i.bak 's/^plugins=(/plugins=(errormux /' ~/.zshrc
    fi
    
    info "Oh My Zsh plugin installed. Add 'errormux' to your plugins array."
fi
```

### Manual Install Instructions

Add to README:

```markdown
## Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/kartikparsoya-eng/ErrorMux.git ~/.errormux
   ```

2. Add to ~/.zshrc:
   ```bash
   echo 'source ~/.errormux/errormux.plugin.zsh' >> ~/.zshrc
   ```

3. Install Python dependencies:
   ```bash
   cd ~/.errormux && uv sync
   ```

4. Restart zsh or run:
   ```bash
   source ~/.zshrc
   ```
```

---

## Integration Point 4: GitHub Polish

### README Structure

```markdown
# ErrorMux

[![Tests](https://github.com/kartikparsoya-eng/ErrorMux/actions/workflows/test.yml/badge.svg)]()
[![Coverage](https://img.shields.io/badge/coverage-92%25-green)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

> On-demand shell error explanations, powered by local AI.

![](demo.gif)

## Features

- **On-demand**: Only when you type `??`, no interrupting your flow
- **Local-first**: Runs entirely on your machine via Ollama
- **Cached**: 7-day TTL, instant responses for repeated errors
- **Smart filtering**: Skips false positives (grep exit 1, test failures)

## Requirements

- zsh 5.9+
- Python 3.12+
- [Ollama](https://ollama.ai) with `gemma4:e2b` model

## Installation

### Oh My Zsh (recommended)

```bash
git clone https://github.com/kartikparsoya-eng/ErrorMux.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/errormux
```

Add `errormux` to your plugins array in `~/.zshrc`:
```bash
plugins=(... errormux)
```

### One-line install

```bash
curl -sSL https://raw.githubusercontent.com/kartikparsoya-eng/ErrorMux/main/install.sh | bash
```

### Manual

See [Manual Installation](#manual-installation) below.

## Usage

1. Run a command that fails:
   ```bash
   $ grep pattern missing-file.txt
   grep: missing-file.txt: No such file or directory
   ```

2. Press `Ctrl+X ?` (or your configured binding)

3. Get an explanation:
   ```
   WHY: The file 'missing-file.txt' does not exist in the current directory.
   FIX: ls *.txt  # List available .txt files
   ```

## Configuration

| Setting | Default | Location |
|---------|---------|----------|
| Model | `gemma4:e2b` | `~/.shell-explainer/config.toml` |
| Cache TTL | 7 days | `~/.shell-explainer/cache.db` |
| Key binding | `Ctrl+X ?` | `errormux.plugin.zsh` |

## Development

```bash
# Clone and setup
git clone https://github.com/kartikparsoya-eng/ErrorMux.git
cd ErrorMux
uv sync

# Run tests
uv run pytest

# Run CLI directly
uv run errormux explain
```

## License

MIT
```

### Demo GIF Creation

Use `asciinema` or `terminalizer`:

```bash
# Record demo
asciinema rec demo.cast

# Convert to GIF
agg demo.cast demo.gif

# Or use terminalizer
terminalizer record demo
terminalizer render demo -o demo.gif
```

### LICENSE File

Create MIT LICENSE:

```
MIT License

Copyright (c) 2026 Kartik Parsoya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Test Badges

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v4
        
      - name: Set up Python
        run: uv python install 3.12
        
      - name: Install dependencies
        run: uv sync
        
      - name: Run tests
        run: uv run pytest
```

---

## Component Integration Matrix

| Component | Widget Fix | Model Switch | Packaging | GitHub Polish |
|-----------|------------|--------------|-----------|---------------|
| `errormux.plugin.zsh` | **MODIFY** | - | - | - |
| `client.py` | - | **MODIFY** | - | - |
| `install.sh` | - | - | **MODIFY** | - |
| `README.md` | - | - | **MODIFY** | **MODIFY** |
| `LICENSE` | - | - | **CREATE** | **CREATE** |
| `.github/workflows/test.yml` | - | - | - | **CREATE** |
| `demo.gif` | - | - | - | **CREATE** |

---

## Build Order

Dependencies between changes are minimal. Recommended order:

1. **Model switch** (1 min) - Simplest, no dependencies
   - Change `OLLAMA_MODEL` in `client.py`
   - Update README requirement section

2. **Widget exit fix** (10 min) - Test locally
   - Add `zle reset-prompt` and `zle -R`
   - Test with failed commands
   - No other components affected

3. **Packaging** (30 min) - Structural changes
   - Update `install.sh` for Oh My Zsh detection
   - Add manual install docs to README
   - No code changes required

4. **GitHub polish** (20 min) - Final touch
   - Create LICENSE
   - Rewrite README
   - Create demo GIF
   - Add GitHub Actions workflow

**Total estimate:** ~60 minutes

---

## New Components to Create

| File | Purpose | Lines |
|------|---------|-------|
| `LICENSE` | MIT license | 21 |
| `.github/workflows/test.yml` | CI test badge | 20 |
| `demo.gif` | Visual demonstration | binary |

## Components to Modify

| File | Changes |
|------|---------|
| `errormux.plugin.zsh` | Add `zle reset-prompt` after `errormux` call |
| `src/errormux/client.py` | Change `OLLAMA_MODEL` constant |
| `install.sh` | Add Oh My Zsh detection and install |
| `README.md` | Complete rewrite with full docs |
| `pyproject.toml` | Update version to 1.1.0 |

---

## Anti-Patterns to Avoid

### Widget Exit

**Don't** use `zle accept-line` - this executes whatever is in the buffer.

**Don't** call `zle` without `reset-prompt` - output from Python corrupts display.

### Packaging

**Don't** use `$ZSH/plugins/` for third-party plugins - only for bundled OMZ plugins.

**Don't** modify `.zshrc` without backup - use `sed -i.bak` or create new file.

**Don't** hardcode paths - use `$HOME` or `$ZSH_CUSTOM` variables.

---

## Data Flow After Widget Fix

```
[User types command]
        ↓
[preexec hook] → captures $3 (command text), redirects stderr
        ↓
[Command fails] → exit code != 0
        ↓
[precmd hook] → captures exit code, stderr, writes to /tmp files
        ↓
[User presses Ctrl+X ?] → zle widget invoked
        ↓
[_errormux_explain] → reads /tmp files, calls Python CLI
        ↓
[errormux CLI] → checks cache, calls Ollama, displays WHY/FIX
        ↓
[zle reset-prompt] → re-expands and redisplays prompt (NEW)
        ↓
[zle -R] → clears any display artifacts (NEW)
        ↓
[Widget returns] → prompt is clean, ready for input ✓
```

---

## Confidence Assessment

| Area | Confidence | Reason |
|------|------------|--------|
| Widget exit fix | HIGH | zle documentation verified, standard pattern |
| Model switch | HIGH | One-line change, no complexity |
| Oh My Zsh packaging | HIGH | Official OMZ docs verified, common pattern |
| README structure | HIGH | Industry standard format |
| Demo GIF creation | MEDIUM | Requires external tools (asciinema/terminalizer) |

---

## Sources

- [zsh ZLE Documentation](https://zsh.sourceforge.io/Doc/Release/Zsh-Line-Editor.html) — Official zsh docs (HIGH confidence)
- [Oh My Zsh Plugins Wiki](https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins) — Plugin structure reference (HIGH confidence)
- [Oh My Zsh git.plugin.zsh](https://github.com/ohmyzsh/ohmyzsh/blob/master/plugins/git/git.plugin.zsh) — Example plugin structure (HIGH confidence)
- [ollama-python](https://github.com/ollama/ollama-python) — Model configuration in client (HIGH confidence)
- Project source code — Existing implementation verified (HIGH confidence)

---

*Architecture research for: ErrorMux v1.1 milestone (widget fix, model switch, packaging, polish)*
*Researched: 2026-04-16*
