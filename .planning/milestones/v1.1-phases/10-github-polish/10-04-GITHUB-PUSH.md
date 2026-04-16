---
phase: 10
plan: 04
name: GitHub Push and Release
type: auto
subsystem: release
tags: [git, github, release, tag]
depends_on: [10-01, 10-02]
---

# Plan 10-04: Push to GitHub with Release

## Objective

Push all changes to GitHub, create v1.1.0 tag, and publish GitHub Release.

## Context

- Branch: main
- Tag: v1.1.0
- Requires: gh CLI authenticated

## Tasks

### Task 1: Verify git status

**Type:** auto

**Action:** Check all changes are committed

**Command:** `git status`

### Task 2: Push to main branch

**Type:** auto

**Action:** Push all commits to origin/main

**Command:** `git push origin main`

### Task 3: Create annotated tag

**Type:** auto

**Action:** Create v1.1.0 tag with release message

**Command:** `git tag -a v1.1.0 -m "Release v1.1.0: First public release

Features:
- On-demand error explanations via ?? command
- Local Gemma model integration (gemma4:e2b)
- Smart skip-list for false positives
- Cache-backed performance (7-day TTL)
- Auto-return to clean prompt
- Multiple installation methods (Oh My Zsh, one-line, manual)
- Configuration via TOML
- Uninstall script"`

### Task 4: Push tag to remote

**Type:** auto

**Action:** Push tag to origin

**Command:** `git push origin v1.1.0`

### Task 5: Create GitHub Release

**Type:** auto

**Action:** Create GitHub Release using gh CLI

**Command:** `gh release create v1.1.0 --title "v1.1.0 - First Public Release" --notes-file - << 'EOF'
## ErrorMux v1.1.0

A zsh plugin that explains shell command failures on-demand using a local Gemma model.

### Installation

**One-line install:**
\`\`\`bash
curl -sSL https://raw.githubusercontent.com/kartikparsoya-eng/ErrorMux/main/install.sh | bash
\`\`\`

**Oh My Zsh:**
\`\`\`bash
git clone https://github.com/kartikparsoya-eng/ErrorMux.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/errormux
# Add 'errormux' to plugins in ~/.zshrc
\`\`\`

### Requirements
- zsh
- Python 3.12+
- uv package manager
- Ollama with gemma4:e2b model

### What's New
- On-demand error explanations via \`??\` command
- Local Gemma model integration (offline-first)
- Smart skip-list for common false positives
- Cache-backed performance (7-day TTL)
- Auto-return to clean prompt after explanation
- Multiple installation methods

### Full Changelog
See commit history for complete details.
EOF`

## Verification

- main branch pushed to origin
- v1.1.0 tag exists locally and remotely
- GitHub Release visible at https://github.com/kartikparsoya-eng/ErrorMux/releases/tag/v1.1.0

## Output

- All changes pushed
- Tag created and pushed
- GitHub Release published
