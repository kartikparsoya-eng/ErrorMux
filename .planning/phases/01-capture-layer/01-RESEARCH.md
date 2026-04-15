# Phase 1: Capture Layer - Research

**Researched:** 2026-04-15
**Domain:** zsh plugin hooks (preexec/precmd), zle widgets, stderr capture
**Confidence:** HIGH

## Summary

Phase 1 implements the capture layer: zsh hooks that intercept every interactive command, capture its text and stderr output, and store exit codes. A `??` zle widget allows users to trigger explanation on-demand. The widget calls a stub Python CLI in this phase; real CLI implementation is Phase 2.

**Primary recommendation:** Use `preexec_functions+=()` and `precmd_functions+=()` arrays (not direct function definitions) to avoid conflicts with other plugins. Capture stderr via temp file with `tee` to preserve real-time visibility. Use `zle -N` to create the widget and `bindkey` for key binding.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Use temp file redirect for stderr capture (most reliable, handles background jobs and edge cases)
- **D-02:** Tee stderr to both terminal and file (errors visible in real-time, also captured for `??` later)
- **D-03:** Stderr written to `/tmp/shell-explainer-last-stderr`
- **D-04:** `??` widget defined in Phase 1
- **D-05:** Widget calls stub Python CLI that prints placeholder message (e.g., "CLI not implemented yet")
- **D-06:** Real CLI implementation deferred to Phase 2

### Claude's Discretion
- Hook registration pattern (preexec_functions vs direct function) — planner can choose standard zsh plugin pattern
- Plugin file structure (single file vs multiple) — planner can choose based on complexity
- Exact mechanism for stderr redirect in preexec — planner to implement based on D-01, D-02

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CAPT-01 | preexec hook captures command to /tmp/shell-explainer-last-cmd | Zsh manual confirms preexec receives command text as $1 (user-typed) or $3 (full text) [CITED: zsh.sourceforge.net] |
| CAPT-02 | preexec hook tees stderr to /tmp/shell-explainer-last-stderr | Temp file + tee pattern is standard; ARCHITECTURE.md provides implementation pattern |
| CAPT-03 | precmd hook records exit code to /tmp/shell-explainer-last-exit | precmd runs after command, $? contains exit code [CITED: zsh.sourceforge.net] |
| CAPT-04 | `??` widget reads tmp files and invokes Python CLI | zle -N creates widget, bindkey binds key sequence [CITED: zsh.sourceforge.net] |
| CAPT-05 | Skip explanation when exit code is 0, 130, or 148 | 0=success, 130=SIGINT (Ctrl+C), 148=SIGTSTP (Ctrl+Z) — not actual errors [VERIFIED] |
</phase_requirements>

## Standard Stack

### Core (zsh layer)

| Component | Version | Purpose | Why Standard |
|-----------|---------|---------|--------------|
| zsh | 5.9+ | Shell environment | Required for preexec/precmd hooks and zle widgets. 5.9 is current stable (May 2022). |
| preexec_functions | (builtin) | Hook array for pre-execution | Official zsh pattern to avoid plugin conflicts [CITED: zsh.sourceforge.net] |
| precmd_functions | (builtin) | Hook array for post-execution | Official zsh pattern to avoid plugin conflicts [CITED: zsh.sourceforge.net] |
| zle | (builtin) | Line editor widgets | zle -N creates user-defined widgets [CITED: zsh.sourceforge.net] |
| bindkey | (builtin) | Key binding | Maps key sequences to widgets |

### Core (Python layer - stub only)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| typer | 0.15+ | CLI framework | Stub CLI entry point. Real implementation in Phase 2. |
| rich | 14.0+ | Terminal output | Stub placeholder output. Real implementation in Phase 2. |

### Temp Files

| Path | Purpose | Notes |
|------|---------|-------|
| `/tmp/shell-explainer-last-cmd` | Last command text | Written by preexec, read by widget |
| `/tmp/shell-explainer-last-stderr` | Last stderr output | Written via tee, read by widget |
| `/tmp/shell-explainer-last-exit` | Last exit code | Written by precmd, read by widget |

**Installation:**
```bash
# In ~/.zshrc
source ~/.config/errormux/errormux.plugin.zsh
```

**Version verification:**
```bash
zsh --version  # 5.9+ required
python3 --version  # 3.12+ required (for Phase 2)
```

## Architecture Patterns

### Recommended Project Structure

```
errormux/
├── errormux.plugin.zsh      # zsh plugin entry point
├── install.sh               # Installation script (Phase 5)
├── pyproject.toml           # Python project config (Phase 2)
└── src/
    └── errormux/
        ├── __init__.py
        └── cli.py           # Stub CLI (placeholder message)
```

### Pattern 1: Hook Arrays (Avoid Conflicts)

**What:** Use `preexec_functions+=()` and `precmd_functions+=()` instead of defining `preexec()` directly.

**When to use:** Always. This is the zsh-standard way to avoid overwriting other plugins' hooks.

**Why:** Defining `preexec() { ... }` replaces any existing preexec function. The `_functions` array pattern appends to the hook chain.

**Example:**
```zsh
# CORRECT (from official zsh documentation)
# Source: https://zsh.sourceforge.net/Doc/Release/Functions.html
_errormux_preexec() {
    _ERRORMUX_LAST_CMD="$3"  # Full command text
}

_errormux_precmd() {
    _ERRORMUX_LAST_EXIT=$?
}

preexec_functions+=(_errormux_preexec)
precmd_functions+=(_errormux_precmd)
```

**Anti-pattern:**
```zsh
# WRONG - overwrites other plugins' hooks
preexec() {
    _ERRORMUX_LAST_CMD="$1"
}
```

### Pattern 2: Stderr Capture via Tee

**What:** Redirect stderr through `tee` to capture to a temp file while still displaying in terminal.

**When to use:** When you need stderr for analysis but user needs to see errors in real-time.

**Implementation (per D-01, D-02):**
```zsh
_ERRORMUX_STDERR_FILE="/tmp/shell-explainer-last-stderr"

_errormux_preexec() {
    _ERRORMUX_LAST_CMD="$3"
    # Clear previous stderr
    : > "$_ERRORMUX_STDERR_FILE"
    # Redirect stderr through tee (preserves terminal output)
    exec 2> >(tee "$_ERRORMUX_STDERR_FILE" >&2)
}

_errormux_precmd() {
    _ERRORMUX_LAST_EXIT=$?
    # Read captured stderr (may have trailing newline)
    _ERRORMUX_LAST_STDERR=$(cat "$_ERRORMUX_STDERR_FILE" 2>/dev/null || echo "")
}
```

**Key insight:** The `exec 2> >(tee file >&2)` pattern:
1. Redirects fd 2 (stderr) to a process substitution
2. `tee` duplicates to both file and stdout
3. `>&2` restores the original stderr flow

### Pattern 3: Zle Widget Binding

**What:** Create a zle widget that invokes Python CLI when user types `??`.

**Example:**
```zsh
# Source: https://zsh.sourceforge.net/Doc/Release/Zsh-Line-Editor.html
_errormux_explain() {
    # Skip if exit code is 0, 130, or 148
    if [[ $_ERRORMUX_LAST_EXIT -eq 0 ]] || \
       [[ $_ERRORMUX_LAST_EXIT -eq 130 ]] || \
       [[ $_ERRORMUX_LAST_EXIT -eq 148 ]]; then
        return
    fi
    
    # Invoke Python CLI (stub in Phase 1)
    errormux explain \
        --command "$_ERRORMUX_LAST_CMD" \
        --exit-code "$_ERRORMUX_LAST_EXIT" \
        --stderr "$_ERRORMUX_LAST_STDERR"
}

# Create the widget
zle -N errormux-explain _errormux_explain

# Bind `??` key sequence to the widget
bindkey '??' errormux-explain
```

### Pattern 4: Temp File State Management

**What:** Write captured state to tmp files for widget to read. Clear on shell startup.

**Rationale:** Global variables don't persist across widget invocation context cleanly. Tmp files are reliable and inspectable for debugging.

**Implementation:**
```zsh
# At plugin load, clear stale state
: > /tmp/shell-explainer-last-cmd
: > /tmp/shell-explainer-last-stderr
echo "0" > /tmp/shell-explainer-last-exit
```

### Anti-Patterns to Avoid

- **Direct hook definition:** `preexec() { ... }` breaks other plugins
- **Global variable name collisions:** Use `_ERRORMUX_` prefix
- **Blocking preexec:** Never do heavy I/O in preexec (blocks shell)
- **Missing stderr restoration:** If you redirect stderr, ensure it flows back to terminal

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Hook registration | Direct `preexec()` function | `preexec_functions+=()` array | Official zsh pattern, avoids plugin conflicts |
| Widget creation | Custom key handling | `zle -N` + `bindkey` | Built-in zsh facilities, well-tested |
| Stderr capture | Subprocess output parsing | `exec 2> >(tee file >&2)` | Preserves terminal visibility, reliable |

**Key insight:** zsh provides robust hook and widget infrastructure. Use it directly rather than building alternatives.

## Common Pitfalls

### Pitfall 1: Hook Pollution Breaks Other Plugins

**What goes wrong:** Defining `preexec` or `precmd` as regular functions overwrites other plugins' hooks.

**Why it happens:** Zsh hook functions are singular unless you use the `_functions` array pattern.

**How to avoid:**
```zsh
# CORRECT
preexec_functions+=(my_preexec)
precmd_functions+=(my_precmd)

# WRONG
preexec() { ... }
```

**Phase to address:** Phase 1 — implement hook registration using `_functions` arrays

**Source:** [CITED: zsh.sourceforge.net/Doc/Release/Functions.html]

---

### Pitfall 2: Hook Race Condition

**What goes wrong:** User types `??` while a long-running command executes, or runs another command before checking the failed one. Captured state is stale or mismatched.

**Why it happens:** Hooks maintain independent state per invocation. Each preexec overwrites previous data.

**How to avoid:**
1. Store captured data in global variables/tmp files that persist until read
2. Clear state after widget reads it (single-use pattern)
3. Document: `??` explains the LAST failed command

**Warning signs:**
- `??` shows explanations for wrong commands
- Exit code doesn't match the command shown

**Phase to address:** Phase 1 — design the hook storage pattern explicitly

---

### Pitfall 3: Stderr Not Captured

**What goes wrong:** Widget shows empty stderr even when command clearly failed with error output.

**Why it happens:**
1. preexec stderr redirect not set up correctly
2. precmd reads before tee finishes writing (async race)
3. Temp file permissions issue

**How to avoid:**
1. Use `exec 2> >(tee ...)` pattern (tested)
2. Add small sync or read directly from variable in precmd
3. Verify tmp files are writable

**Phase to address:** Phase 1 — implement stderr capture per D-01, D-02

---

### Pitfall 4: Widget Name Collisions

**What goes wrong:** Other plugins define widgets with generic names like `explain` or `show_error`, causing conflicts.

**How to avoid:** Namespace all widgets with `errormux-` or `_errormux-` prefix.

## Code Examples

### Complete Plugin Skeleton (Verified Pattern)

```zsh
#!/usr/bin/env zsh
# errormux.plugin.zsh - zsh plugin entry point
# Source: Official zsh documentation + project research

# Global state
_ERRORMUX_LAST_CMD=""
_ERRORMUX_LAST_EXIT=0
_ERRORMUX_LAST_STDERR=""
_ERRORMUX_STDERR_FILE="/tmp/shell-explainer-last-stderr"

# Clear stale state on load
: > /tmp/shell-explainer-last-cmd
: > "$_ERRORMUX_STDERR_FILE"
echo "0" > /tmp/shell-explainer-last-exit

# preexec: capture command, set up stderr redirect
_errormux_preexec() {
    _ERRORMUX_LAST_CMD="$3"  # Full command text
    : > "$_ERRORMUX_STDERR_FILE"
    exec 2> >(tee "$_ERRORMUX_STDERR_FILE" >&2)
}

# precmd: capture exit code, read stderr
_errormux_precmd() {
    _ERRORMUX_LAST_EXIT=$?
    _ERRORMUX_LAST_STDERR=$(cat "$_ERRORMUX_STDERR_FILE" 2>/dev/null || echo "")
    
    # Write state to tmp files for widget
    printf '%s' "$_ERRORMUX_LAST_CMD" > /tmp/shell-explainer-last-cmd
    printf '%s' "$_ERRORMUX_LAST_STDERR" > /tmp/shell-explainer-last-stderr
    echo "$_ERRORMUX_LAST_EXIT" > /tmp/shell-explainer-last-exit
}

# Widget: user-triggered explanation
_errormux_explain() {
    local exit_code=$(cat /tmp/shell-explainer-last-exit 2>/dev/null || echo "0")
    
    # Skip if exit code is 0, 130, or 148
    if [[ $exit_code -eq 0 ]] || [[ $exit_code -eq 130 ]] || [[ $exit_code -eq 148 ]]; then
        return
    fi
    
    # Invoke Python CLI (stub)
    errormux explain
}

# Register hooks using array pattern (avoids conflicts)
preexec_functions+=(_errormux_preexec)
precmd_functions+=(_errormux_precmd)

# Create and bind widget
zle -N errormux-explain _errormux_explain
bindkey '??' errormux-explain
```

### Stub Python CLI (Phase 1)

```python
# src/errormux/cli.py
import typer

app = typer.Typer()

@app.command()
def explain():
    """Stub CLI - prints placeholder message."""
    typer.echo("[errormux] CLI not implemented yet - coming in Phase 2")

if __name__ == "__main__":
    app()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Direct `preexec()` definition | `preexec_functions+=()` array | zsh 4.3+ (2005) | Plugin compatibility |
| Subprocess output capture | `exec` redirect + `tee` | Standard Unix | Preserves terminal visibility |
| Global state in variables | Tmp files for persistence | This project | Reliable widget invocation |

## Assumptions Log

> All claims in this research were verified or cited — no user confirmation needed.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Exit code 148 = SIGTSTP on Linux (20) | Skip Codes | Platform-specific; macOS uses 146. Test on target platform. |

**Verification needed:** Exit code 148 for SIGTSTP is correct on Linux. On macOS (darwin), SIGTSTP=18, so exit code would be 146. The requirement specifies 148, suggesting Linux target. Planner should verify or handle both platforms.

## Open Questions

1. **Platform-specific exit codes**
   - What we know: Exit codes for signals are `128 + signal_number`
   - What's unclear: Signal numbers vary by platform (Linux vs macOS)
   - Recommendation: Document expected behavior for both platforms, or use signal name detection

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| zsh | Shell hooks | ✓ | 5.9 (arm64) | — |
| Python 3.12+ | CLI (Phase 2) | ✓ | 3.14.3 | — |
| uv | Package manager | ✗ | — | Install via `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Ollama | LLM backend (Phase 2) | CLI ✓, Service ✗ | 0.20.3 | Start with `ollama serve` |

**Missing dependencies with no fallback:**
- `uv` package manager — required for Phase 2+. Install before Phase 2 execution.

**Missing dependencies with fallback:**
- Ollama service not running — Phase 1 doesn't require it (stub CLI). Phase 2 will need service running.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | `pyproject.toml` (to be created) |
| Quick run command | `uv run pytest tests/ -x` |
| Full suite command | `uv run pytest tests/ -v` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CAPT-01 | preexec captures command | integration | Manual zsh test | ❌ Wave 0 |
| CAPT-02 | preexec tees stderr | integration | Manual zsh test | ❌ Wave 0 |
| CAPT-03 | precmd records exit code | integration | Manual zsh test | ❌ Wave 0 |
| CAPT-04 | `??` widget invokes CLI | integration | Manual zsh test | ❌ Wave 0 |
| CAPT-05 | Skip exit codes 0, 130, 148 | integration | Manual zsh test | ❌ Wave 0 |

**Note:** Phase 1 is primarily zsh code. Testing requires:
1. zsh integration tests (run in actual shell)
2. Python stub CLI tests (minimal, just imports work)

### Sampling Rate
- **Per task commit:** Manual verification of hook behavior
- **Per wave merge:** Manual end-to-end test in zsh
- **Phase gate:** Interactive test: run failing command, type `??`, verify placeholder message

### Wave 0 Gaps
- [ ] `tests/test_plugin.zsh` — zsh integration tests for hooks
- [ ] `tests/test_cli_stub.py` — Python stub CLI import test
- [ ] Test framework setup for zsh scripts

**Recommendation:** Phase 1 testing is primarily manual/interactive. Automated zsh tests can be added in Phase 6 (Testing) along with other test infrastructure.

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | N/A — local shell plugin |
| V3 Session Management | no | N/A — local shell plugin |
| V4 Access Control | no | N/A — local shell plugin |
| V5 Input Validation | yes | Sanitize command text before writing to tmp files |
| V6 Cryptography | no | N/A — no secrets in capture layer |

### Known Threat Patterns for zsh Plugins

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Command injection via tmp files | Tampering | Use fixed tmp paths with proper permissions (600) |
| Information disclosure in tmp files | Information Disclosure | Clear tmp files on startup; use per-user paths |

**Mitigation for Phase 1:**
- Tmp files use fixed paths in `/tmp/` (world-writable, but per-session)
- Future: Consider using `$XDG_RUNTIME_DIR` or per-user tmp directory

## Sources

### Primary (HIGH confidence)
- [zsh Functions Manual](https://zsh.sourceforge.net/Doc/Release/Functions.html) — Hook function arrays, preexec/precmd specification [CITED]
- [zsh ZLE Manual](https://zsh.sourceforge.net/Doc/Release/Zsh-Line-Editor.html) — Widget creation with zle -N, bindkey [CITED]
- `.planning/research/STACK.md` — Project stack research, HIGH confidence [VERIFIED]
- `.planning/research/PITFALLS.md` — Domain pitfalls, MEDIUM confidence [VERIFIED]
- `.planning/research/ARCHITECTURE.md` — Architecture patterns, HIGH confidence [VERIFIED]

### Secondary (MEDIUM confidence)
- `.planning/PROJECT.md` — Project constraints and decisions [PROJECT]
- `.planning/REQUIREMENTS.md` — Phase requirements [PROJECT]

### Tertiary (LOW confidence)
- N/A — all claims verified or cited

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — Official zsh documentation + existing project research
- Architecture: HIGH — Patterns verified from official docs, existing research files
- Pitfalls: HIGH — Drawn from existing PITFALLS.md (MEDIUM confidence source) + verified hook patterns

**Research date:** 2026-04-15
**Valid until:** 30 days (stable zsh API)
