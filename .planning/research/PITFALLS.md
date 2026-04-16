# Domain Pitfalls

**Domain:** zsh plugin + local LLM integration
**Researched:** 2026-04-16 (updated for v1.1)
**Confidence:** HIGH (official docs) / MEDIUM (web-only for zsh specifics)

---

## v1.1 MILESTONE: Widget Exit, Model Switch, Packaging, Polish

*Pitfalls specific to adding these features to existing system.*

### Pitfall: Widget Doesn't Return to Prompt After Output

**What goes wrong:**
After the `??` widget displays output, the user must press Enter manually to get back to a working prompt. This breaks the expected "one keystroke" UX and feels broken.

**Why it happens:**
ZLE widgets that call external commands (like Python CLI) don't automatically re-render the prompt. The widget completes but leaves the terminal in a state where the prompt is stale. The fix requires calling `zle reset-prompt` AND ensuring the widget is properly registered.

**How to avoid:**
```zsh
# WRONG - widget exits without refresh
_explain_error() {
    python -m errormux.cli
}

# CORRECT - refresh prompt after widget
_explain_error() {
    python -m errormux.cli
    zle reset-prompt
}
zle -N _explain_error
bindkey '^X?' _explain_error
```

**Warning signs:**
- After pressing `??`, you see output but no fresh prompt
- Terminal appears "stuck" until you press Enter
- Prompt shows stale directory/state information

**Phase to address:** Widget fix phase (first phase of v1.1)

---

### Pitfall: Model Name Mismatch After Switching to gemma4:e2b

**What goes wrong:**
Code references `gemma3:4b` but Ollama only has `gemma4:e2b` pulled. Requests fail with "model not found", or worse, Ollama silently pulls the wrong model.

**Why it happens:**
- Model names are strings scattered across codebase (config, CLI defaults, tests)
- `gemma4:e2b` is the EXACT tag name — not `gemma4:e2b-it` or `gemma4:2b`
- The model must be pulled first: `ollama pull gemma4:e2b`
- Tests may mock with wrong model names

**How to avoid:**
1. Centralize model name in one config location:
   ```python
   # config.py - single source of truth
   DEFAULT_MODEL = "gemma4:e2b"
   ```
2. Verify model is available at startup or provide clear error:
   ```python
   def check_model_available(model_name: str) -> bool:
       try:
           ollama.show(model_name)
           return True
       except ollama.ResponseError:
           return False
   ```
3. Update all test mocks to use same constant
4. Document required model in README: `ollama pull gemma4:e2b`

**Warning signs:**
- "model 'gemma3:4b' not found" errors
- First request takes much longer (Ollama auto-pulling)
- Tests fail with unexpected model responses

**Phase to address:** Model switch phase (second phase of v1.1)

---

### Pitfall: Oh My Zsh Installation Path Wrong

**What goes wrong:**
Plugin installs to wrong directory, Oh My Zsh can't find it, or conflicts with existing plugin of same name.

**Why it happens:**
- Oh My Zsh expects plugins in `$ZSH_CUSTOM/plugins/` (NOT `$ZSH/plugins/`)
- Plugin directory name must match the plugin name exactly
- Users may have `$ZSH_CUSTOM` undefined or pointing elsewhere
- The `.plugin.zsh` file naming is REQUIRED

**How to avoid:**
```bash
# CORRECT Oh My Zsh installation
# Plugin name: errormux
# Structure:
#   ~/.oh-my-zsh/custom/plugins/errormux/
#     ├── errormux.plugin.zsh  (REQUIRED naming)
#     ├── errormux-cli.py
#     └── ...

# Installation script should:
OMZ_PLUGINS_DIR="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins"
mkdir -p "$OMZ_PLUGINS_DIR/errormux"
# Copy files to $OMZ_PLUGINS_DIR/errormux/

# Verify in user's .zshrc:
# plugins=(... errormux)
```

**Warning signs:**
- `plugins=(errormux)` in .zshrc but plugin doesn't load
- "command not found" for plugin functions
- Plugin loads on one machine but not another

**Phase to address:** Packaging phase (third phase of v1.1)

---

### Pitfall: Cache Keys Become Invalid After Model Switch

**What goes wrong:**
After switching to gemma4:e2b, cached explanations from gemma3:4b are returned. These may be wrong because different models produce different outputs for same input.

**Why it happens:**
Cache key is based on (command + stderr + exit_code) but doesn't include model name. Old cache entries persist through model switch.

**How to avoid:**
Include model name in cache key:
```python
def cache_key(command: str, stderr: str, exit_code: int, model: str) -> str:
    data = f"{command}|{stderr}|{exit_code}|{model}"
    return hashlib.sha256(data.encode()).hexdigest()
```

Or invalidate cache on model switch:
```python
CACHE_VERSION = "v2-gemma4"  # Bump when model changes

def cache_key(...):
    data = f"{CACHE_VERSION}|{command}|{stderr}|{exit_code}"
    return hashlib.sha256(data.encode()).hexdigest()
```

**Warning signs:**
- Explanations don't match new model's style
- First-run explanations differ from cached ones
- Tests pass but real usage shows different behavior

**Phase to address:** Model switch phase (second phase of v1.1)

---

### Pitfall: Demo GIF Doesn't Capture Terminal Correctly

**What goes wrong:**
Demo GIF shows garbled text, wrong colors, or doesn't demonstrate the key feature (explaining errors). Wastes users' time and hurts adoption.

**Why it happens:**
- Terminal recording tools have quirks with zsh prompts
- Recording captures at wrong resolution
- The `??` keybinding needs visible demonstration
- Rich library output may not render well in GIFs

**How to avoid:**
Use proper terminal recording tools:
```bash
# Recommended: asciinema + agg for GIF
asciinema rec demo.cast
# Run demonstration
agg demo.cast demo.gif

# Alternative: terminalizer
terminalizer record -k demo
terminalizer render demo
```

Demo script should:
1. Show a command that fails (e.g., `grep nonexistent file.txt`)
2. Press the keybinding (Ctrl+X ?)
3. Show the explanation appearing
4. Show prompt returning cleanly

**Warning signs:**
- GIF shows `??` literally instead of triggering
- Colors are wrong or text is unreadable
- File size is huge (>2MB)

**Phase to address:** Polish phase (fourth phase of v1.1)

---

### Pitfall: Multiple Install Methods Conflict

**What goes wrong:**
User installs via git clone, then tries Oh My Zsh method. Old files interfere, or PATH points to wrong location.

**How to avoid:**
- Add `uninstall.sh` script that cleans all methods
- Check for existing installation before installing
- Document that only ONE method should be used

**Phase to address:** Packaging phase

---

### Pitfall: Badge URLs Become Stale

**What goes wrong:**
README shows "build passing" but CI is broken, or version badge points to wrong version.

**How to avoid:**
- Use shields.io dynamic badges that pull from GitHub API
- Test badges locally before pushing
- Example: `![Tests](https://github.com/user/repo/actions/workflows/test.yml/badge.svg)`

**Phase to address:** Polish phase

---

### Pitfall: LICENSE File Missing or Wrong

**What goes wrong:**
Repository has no LICENSE, or uses incompatible license.

**How to avoid:**
- Add LICENSE file before first public push
- MIT is recommended for zsh plugins (simple, permissive)
- Use SPDX identifier: `SPDX-License-Identifier: MIT`

**Phase to address:** Polish phase

---

## v1.0 MILESTONE: Core Plugin Architecture

*Pitfalls from initial implementation (preserved for reference).*

### Pitfall: preexec/precmd Hook Race Condition

**What goes wrong:**
The `preexec` hook captures command text before execution, but `precmd` captures the exit code after. If the user types `??` while a long-running command is still executing (or if another command was run in between), the captured state is stale or mismatched.

**Why it happens:**
Developers assume hooks maintain state across invocations. In reality, each hook call is independent. A user might run `make build`, then immediately run `echo test` before checking the build failure — now `??` sees the wrong command.

**How to avoid:**
Store captured data in global variables that persist until read. Use a single-use flag pattern: preexec sets `_ERRORMUX_LAST_CMD`, precmd sets `_ERRORMUX_LAST_EXIT` and `_ERRORMUX_LAST_STDERR`. The `??` widget reads and clears these atomically, preventing stale reads.

**Warning signs:**
- `??` shows explanations for wrong commands
- Exit code doesn't match the command shown
- Empty or "command not found" when user expects an error explanation

**Phase to address:** Phase 1 (Capture Layer) — design the hook storage pattern explicitly

---

### Pitfall: Ollama Connection Timeout Blocks Shell

**What goes wrong:**
When Ollama is slow to respond (model loading, heavy inference), the shell freezes for up to 10 seconds. Users think the terminal crashed.

**Why it happens:**
The Python CLI makes a blocking HTTP request to `localhost:11434`. Without proper timeout handling, the default socket timeout can be indefinite. Even with a 10s timeout, that's an eternity in shell-interactive time.

**How to avoid:**
1. Set explicit timeout on all httpx requests (the project already specifies 10s max)
2. Show immediate feedback ("Thinking...") before the blocking call
3. Implement graceful degradation: on timeout, show "Ollama timeout — try again?" instead of hanging
4. Consider a background pre-fetch: when preexec detects an error, start loading the model asynchronously so it's warm when `??` is called

**Warning signs:**
- Shell freezes for multiple seconds after typing `??`
- User reports "terminal hung" when first using the tool after Ollama restart
- `top` shows Python process waiting on network I/O

**Phase to address:** Phase 2 (Python CLI) — implement timeout with proper error handling and user feedback

---

### Pitfall: Skip-List False Positives

**What goes wrong:**
Commands like `grep pattern file` exit 1 when no match is found, but that's not an error — it's expected behavior. Similarly, `test -f missing` and `diff old new` use exit 1 semantically, not as failures. The plugin tries to explain these "errors" and produces useless or confusing output.

**Why it happens:**
Exit code 1 is ambiguous: it can mean "error" or "false/nomatch/not found". Developers assume non-zero = error without considering semantic exit codes.

**How to avoid:**
Implement a skip-list that checks:
1. Command name against known non-error commands (grep, test, [, diff, git diff, find)
2. Context: if `grep` exits 1 and stderr is empty, it's "no match", not error
3. Allow users to extend the skip-list in `config.toml`

The skip-list should be checked BEFORE calling Ollama, not after.

**Warning signs:**
- `??` explains "grep: no matches found" as if it's an error
- User gets explanations for intentional exit codes (test conditions)
- Gemma generates confused explanations like "The command succeeded but returned 1"

**Phase to address:** Phase 1 (Capture Layer) — define skip-list as a core component; Phase 4 (Skip-list) — implement fully

---

### Pitfall: Cache Poisoning via Similar Commands

**What goes wrong:**
The cache keys on SHA256 of (command + exit_code + stderr_excerpt). But `npm install` failing due to network and `npm install` failing due to permission issues produce similar keys — wrong explanation returned.

**Why it happens:**
Stderr is truncated or normalized too aggressively, losing distinguishing context. Or stderr isn't included in the key at all.

**How to avoid:**
Include full (or first N chars of) stderr in the cache key. Don't truncate stderr for key generation — truncate only for LLM prompt context. Consider including working directory if errors are path-relative.

**Warning signs:**
- Same command in different directories returns cached explanation for wrong context
- Permission error returns network error explanation from cache
- User runs same command twice with different failures, gets identical explanation

**Phase to address:** Phase 3 (Caching) — design cache key to include stderr and potentially cwd

---

### Pitfall: Hook Function Pollution Breaks Other Plugins

**What goes wrong:**
Defining `preexec` or `precmd` as regular functions overwrites other plugins' hooks. If another plugin had its own preexec, it stops working.

**Why it happens:**
Zsh hook functions are singular unless you use the `_functions` array pattern. Defining `preexec() { ... }` replaces any existing `preexec`.

**How to avoid:**
Use the hook array pattern documented in Zsh manual:
```zsh
preexec_functions+=(errorMux_preexec)
precmd_functions+=(errorMux_precmd)
```
This appends to the hook chain rather than replacing it. On plugin unload, remove from the array.

**Warning signs:**
- Other plugins stop working after ErrorMux loads
- `git` plugin status updates disappear
- History plugins lose track of commands

**Phase to address:** Phase 1 (Capture Layer) — implement hook registration using `_functions` arrays

---

### Pitfall: Python Dependency Hell in Shell Context

**What goes wrong:**
The plugin's Python CLI depends on `httpx`, `typer`, `rich`. If the user doesn't have these installed, or has incompatible versions, `??` fails with import errors.

**Why it happens:**
Shell plugins run in the user's environment. Unlike standalone apps, they can't bundle dependencies easily. Users may have different Python versions, different package managers (pip vs uv vs conda), or conflicts with existing packages.

**How to avoid:**
1. Use `uv` for dependency management (already specified in project) — it handles isolation better than pip
2. Bundle a `requirements.txt` or `pyproject.toml` with pinned versions
3. The install script should check: `python3 --version`, `uv --version`, and fail fast with helpful messages
4. Consider a fallback: if deps fail, show a clear "Run install script" message instead of a traceback

**Warning signs:**
- `??` prints `ModuleNotFoundError: No module named 'httpx'`
- Python traceback obscures the actual issue
- Works in one terminal but not another (different environment)

**Phase to address:** Phase 5 (Installation) — robust install script with dependency verification

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip caching, always call Ollama | Faster implementation, simpler code | Slow UX, Ollama overload, wasted tokens | Never — caching is core value |
| Hardcode model name | No config complexity | Can't use different models, breaks if model renamed | Prototype only, replace before MVP |
| Ignore stderr, only look at exit code | Simpler prompt construction | Misses critical error context, poor explanations | Never |
| Synchronous-only (no background pre-fetch) | Simpler implementation | Cold Ollama = long first-call latency | MVP acceptable, improve later |

---

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Ollama HTTP API | Assume localhost:11434 always available | Check connectivity first, show helpful error if Ollama not running |
| Ollama streaming | Ignore stream mode, block on full response | Use `stream: false` for simplicity in MVP, but handle streaming for long responses |
| Ollama model switch | Use old model name after switch | Centralize model name, verify model available at startup |
| SQLite cache | Use single-threaded access, ignore concurrency | SQLite handles concurrent reads fine; serialize writes or use WAL mode |
| Zsh variables | Use global names like `LAST_CMD` that might conflict | Prefix all globals with `_ERRORMUX_` to avoid collisions |
| zsh widget | Forget to call `zle reset-prompt` | Always refresh prompt after widget output |
| Oh My Zsh | Install to `$ZSH/plugins/` instead of `$ZSH_CUSTOM/plugins/` | Use `$ZSH_CUSTOM/plugins/` for user plugins |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Unbounded cache growth | Cache.db grows to GB, slow lookups | Implement 7-day TTL cleanup; add size cap | Months of use without cleanup |
| Prompt too long | Ollama rejects request, or slow inference | Truncate command/stderr to reasonable length (e.g., 500 chars each) | User runs 1000-char piped command |
| Hook does heavy work | Shell lag on every command | Keep hooks minimal: only capture data, no processing until `??` called | Hooks contain network calls or file I/O |

---

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Include full stderr in prompt | Sensitive data (passwords, tokens, paths) sent to local LLM | Truncate stderr, warn user if using cloud models (but this project is local-only) |
| Execute commands from LLM output | LLM hallucinates dangerous commands, user blindly runs them | NEVER execute LLM suggestions. Only display them. Clearly mark as suggestions. |
| Store cache in world-readable location | Other users on shared machine see command history | Default cache path `~/.shell-explainer/cache.db` with mode 600 |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Auto-explain on every error | Noisy, interrupts flow, user tunes out | Opt-in via `??` only (already specified) — respects user's workflow |
| Verbose output | Screen clutter, hard to parse | One-sentence WHY, one-sentence FIX, no fluff (already specified) |
| No feedback during Ollama call | User thinks it's broken | Show "Thinking..." spinner during inference |
| Explanation too technical | User doesn't understand "ENOENT" or "SIGSEGV" | Gemma prompt should request plain language, jargon-free explanations |
| Widget doesn't return to prompt | User thinks terminal is broken | Call `zle reset-prompt` after widget output |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

### v1.1 Checklist

- [ ] **Widget fix:** Often missing `zle reset-prompt` — verify prompt refreshes after output
- [ ] **Model switch:** Often missing cache invalidation — verify old cache doesn't return
- [ ] **Packaging:** Often missing `.plugin.zsh` naming — verify Oh My Zsh finds plugin
- [ ] **Demo GIF:** Often missing keybinding demonstration — verify `Ctrl+X ?` is visible
- [ ] **Install docs:** Often missing `ollama pull gemma4:e2b` step — verify fresh install works
- [ ] **LICENSE:** Often missing entirely — verify file exists at repo root

### v1.0 Checklist

- [ ] **Hook capture:** Often missing stderr capture — verify `$ERRORMUX_LAST_STDERR` is set in precmd
- [ ] **Skip-list:** Often missing edge cases (e.g., `git diff`, `test -e`) — verify against real-world command corpus
- [ ] **Cache invalidation:** Often missing TTL enforcement — verify 7-day old entries are purged
- [ ] **Install script:** Often missing Python version check — verify `python3 --version` >= 3.12
- [ ] **Ollama connectivity:** Often missing graceful degradation — verify behavior when Ollama not running

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Widget doesn't return | LOW | Add `zle reset-prompt` line |
| Model mismatch | MEDIUM | Update model name constant, clear cache, update docs |
| Wrong install path | LOW | Move plugin dir to `$ZSH_CUSTOM/plugins/` |
| Invalid cache keys | MEDIUM | Delete cache.db or add version key |
| Bad demo GIF | LOW | Re-record with proper tool (asciinema + agg) |
| Hook race condition | LOW | Clear captured state after read; add timestamp validation |
| Ollama timeout | MEDIUM | Implement timeout + "Ollama slow" message; restart Ollama service |
| Skip-list false positive | MEDIUM | Add command to skip-list; update prompt to handle edge case |
| Cache poisoning | HIGH | Clear cache.db; redesign cache key to include more context |
| Hook pollution | HIGH | Switch to `_functions` array pattern; coordinate with other plugin maintainers |
| Dependency hell | MEDIUM | Re-run install script; check `uv pip list`; verify Python version |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

### v1.1 Phases

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Widget doesn't return | Widget fix | Test: run widget, verify prompt returns |
| Model name mismatch | Model switch | Test: run with fresh Ollama, verify model found |
| Oh My Zsh path wrong | Packaging | Test: install via OMZ, verify plugin loads |
| Cache key invalid | Model switch | Test: switch model, verify new explanations |
| Demo GIF broken | Polish | Test: view GIF in browser, verify readable |
| LICENSE missing | Polish | Test: verify file at repo root |

### v1.0 Phases

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Hook race condition | Phase 1 | Unit test: fast command sequence + `??` shows correct state |
| Ollama timeout | Phase 2 | Integration test: kill Ollama, verify graceful error |
| Skip-list false positives | Phase 4 | Test corpus: 50+ common commands with non-error exit codes |
| Cache poisoning | Phase 3 | Test: same command, different stderr, different explanations |
| Hook pollution | Phase 1 | Test: load ErrorMux + other plugin, verify both hooks work |
| Dependency hell | Phase 5 | Fresh VM install: verify one-command setup works |

---

## Sources

- [Ollama gemma4 library](https://ollama.com/library/gemma4) — Model specs, naming, best practices (HIGH confidence)
- [Oh My Zsh Plugins Wiki](https://github.com/ohmyzsh/ohmyzsh/wiki/Plugins) — Plugin structure, installation (HIGH confidence)
- [Oh My Zsh External Plugins](https://github.com/ohmyzsh/ohmyzsh/wiki/External-plugins) — Installation guidelines (HIGH confidence)
- [Zsh Functions Manual](https://zsh.sourceforge.io/Doc/Release/Functions.html) — Hook function arrays (HIGH confidence)
- [Zsh ZLE Manual](https://zsh.sourceforge.io/Doc/Release/Zsh-Line-Editor.html) — Widget behavior, reset-prompt (MEDIUM confidence)
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md) — Timeout handling, streaming, model loading (HIGH confidence)
- [Ollama Python Library](https://github.com/ollama/ollama-python) — Error handling patterns, ResponseError (HIGH confidence)
- Project Context: .planning/PROJECT.md — ErrorMux architecture and constraints (HIGH confidence)

---
*Pitfalls research for: ErrorMux*
*Updated: 2026-04-16 for v1.1 milestone*
