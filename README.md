# ErrorMux

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Test Coverage](https://img.shields.io/badge/Coverage-0%25-red)](https://github.com/kartikparsoya-eng/ErrorMux)

A zsh plugin that explains shell command failures on-demand. When a command fails, type `??` to get a one-sentence explanation and suggested fix from a local Gemma model (via Ollama).

**Features:**
- Fast, local, offline-first — no cloud dependency
- Cache-backed for speed (7-day TTL)
- Smart skip-list filters false-positive "errors"
- Auto-returns to clean prompt after explanation

## Requirements

- zsh
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Ollama](https://ollama.ai) with `gemma4:e2b` model

## Installation

### Option 1: Oh My Zsh

```bash
# Clone to Oh My Zsh custom plugins
git clone https://github.com/kartikparsoya-eng/ErrorMux.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/errormux

# Add to your plugins array in ~/.zshrc
plugins=(git errormux ...)

# Reload shell
source ~/.zshrc
```

### Option 2: One-Line Install

```bash
curl -sSL https://raw.githubusercontent.com/kartikparsoya-eng/ErrorMux/main/install.sh | bash
```

This script:
- Detects Oh My Zsh and uses the correct path
- Installs Python dependencies via uv
- Configures your .zshrc (or prints instructions for Oh My Zsh)

### Option 3: Manual Install

```bash
# Clone the repository
git clone https://github.com/kartikparsoya-eng/ErrorMux.git ~/.shell-explainer

# Install dependencies
cd ~/.shell-explainer
uv sync

# Add to ~/.zshrc
echo 'source ~/.shell-explainer/errormux.plugin.zsh' >> ~/.zshrc

# Reload shell
source ~/.zshrc
```

## Post-Install Setup

1. Ensure Ollama is running: `ollama serve`
2. Pull the required model: `ollama pull gemma4:e2b`
3. Run a failing command, then type `??`

## Usage

```bash
$ ls /nonexistent
ls: /nonexistent: No such file or directory

$ ??
WHY: Directory does not exist.
FIX: Check the path with 'ls' or create it with 'mkdir -p /nonexistent'
```

## Updating

Re-run the install command:

```bash
# Oh My Zsh
cd ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/errormux && git pull

# One-line
curl -sSL https://raw.githubusercontent.com/kartikparsoya-eng/ErrorMux/main/install.sh | bash

# Manual
cd ~/.shell-explainer && git pull
```

## Uninstalling

```bash
curl -sSL https://raw.githubusercontent.com/kartikparsoya-eng/ErrorMux/main/uninstall.sh | bash
```

Then remove the plugin from your `.zshrc`:
- Oh My Zsh: Remove `errormux` from plugins array
- Manual: Remove the `source ~/.shell-explainer/errormux.plugin.zsh` line

## Configuration

Configuration file: `~/.shell-explainer/config.toml`

```toml
[model]
# Required: Ollama model for explanations
# Install: ollama pull gemma4:e2b
name = "gemma4:e2b"
```

## Files

| File | Purpose |
|------|---------|
| `~/.shell-explainer/config.toml` | Configuration |
| `~/.shell-explainer/cache.db` | Explanation cache (7-day TTL) |

## License

MIT License - see [LICENSE](LICENSE)
