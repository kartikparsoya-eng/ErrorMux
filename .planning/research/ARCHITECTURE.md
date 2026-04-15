# Architecture Research

**Domain:** zsh plugin with Python backend
**Researched:** 2026-04-15
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interaction Layer                   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   `??`       │  │  preexec     │  │  precmd      │       │
│  │   Widget     │  │   Hook       │  │   Hook       │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
├─────────┴─────────────────┴─────────────────┴────────────────┤
│                    zsh Plugin Layer                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐    │
│  │          errormux.plugin.zsh (Entry Point)          │    │
│  │  • Hook registration (preexec/precmd)               │    │
│  │  • Widget binding (`??` keybinding)                 │    │
│  │  • State capture (command, exit code, stderr)       │    │
│  │  • CLI invocation                                   │    │
│  └──────────────────────────┬──────────────────────────┘    │
│                             │                                │
├─────────────────────────────┴────────────────────────────────┤
│                   Python Backend Layer                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  CLI Entry   │  │    Cache     │  │   Ollama     │       │
│  │  (typer)     │  │   (SQLite)   │  │   Client     │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│  ┌──────┴─────────────────┴─────────────────┴───────┐       │
│  │              Core Orchestrator                    │       │
│  │  • Skip-list filtering                           │       │
│  │  • Cache lookup (SHA256 key)                     │       │
│  │  • Prompt construction                           │       │
│  │  • Response formatting (WHY/FIX)                 │       │
│  └──────────────────────────────────────────────────┘       │
├─────────────────────────────────────────────────────────────┤
│                     External Services                        │
│  ┌──────────────────┐  ┌──────────────────────────────┐     │
│  │  Ollama API      │  │  ~/.shell-explainer/cache.db │     │
│  │  localhost:11434 │  │  ~/.shell-explainer/         │     │
│  └──────────────────┘  └──────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `*.plugin.zsh` | Entry point, hook setup, widget registration | Single file sourced by zsh |
| preexec hook | Capture command before execution | Global variable storage |
| precmd hook | Capture exit code and stderr after execution | Exit code in `$?`, stderr via redirection |
| Widget (`??`) | User-triggered explanation request | zle -N widget binding, invokes Python CLI |
| Python CLI | Parse args, orchestrate flow, output result | typer for CLI, rich for formatting |
| Cache layer | 7-day TTL storage, SHA256 key lookup | SQLite with single table |
| Skip-list | Filter false-positive "errors" | Hardcoded patterns + configurable |
| Ollama client | HTTP API calls to local LLM | httpx with streaming, 10s timeout |

## Recommended Project Structure

```
errormux/
├── errormux.plugin.zsh      # Entry point for zsh plugin
├── install.sh               # Installation script
├── pyproject.toml           # Python project config (uv)
├── src/
│   └── errormux/
│       ├── __init__.py
│       ├── cli.py           # typer CLI entry point
│       ├── cache.py         # SQLite cache operations
│       ├── skip_list.py     # False-positive filtering
│       ├── ollama.py        # Ollama API client
│       ├── prompt.py        # LLM prompt construction
│       └── config.py        # Config loading (TOML)
├── tests/
│   ├── test_cache.py
│   ├── test_skip_list.py
│   └── test_prompt.py
└── README.md
```

### Structure Rationale

- **`errormux.plugin.zsh` at root:** Standard zsh plugin convention (Oh My Zsh, zgenom compatible)
- **`src/errormux/` Python package:** Clean import paths, editable install support
- **Separate modules per concern:** Testability, single responsibility
- **`install.sh` at root:** One-line installation for users

## Architectural Patterns

### Pattern 1: Hook-Based State Capture

**What:** Use zsh's `preexec` and `precmd` hooks to capture command context without modifying user workflow.

**When to use:** When you need to react to command execution but don't want to wrap/override shell builtins.

**Trade-offs:** 
- ✅ Non-invasive, works with other plugins
- ✅ Reliable timing (before/after execution)
- ❌ Can't capture stderr without redirection tricks
- ❌ Hook order matters if multiple plugins modify state

**Example:**
```zsh
# In errormux.plugin.zsh
_ERRORMUX_LAST_CMD=""
_ERRORMUX_LAST_EXIT=0
_ERRORMUX_LAST_STDERR=""

errormux_preexec() {
    _ERRORMUX_LAST_CMD="$1"
    _ERRORMUX_LAST_STDERR=""
}

errormux_precmd() {
    _ERRORMUX_LAST_EXIT=$?
}

autoload -Uz add-zsh-hook
add-zsh-hook preexec errormux_preexec
add-zsh-hook precmd errormux_precmd
```

### Pattern 2: Widget-Triggered CLI Invocation

**What:** Bind a zle widget that spawns a Python subprocess, captures output, and displays to user.

**When to use:** On-demand operations (not auto-triggered), user explicitly requests action.

**Trade-offs:**
- ✅ Clear user intent (typed `??`)
- ✅ No performance impact on normal shell use
- ✅ Easy to test CLI independently
- ❌ Process spawn latency (~50-100ms cold start)
- ❌ Need to pass state from shell to Python

**Example:**
```zsh
errormux_explain() {
    # Check if last command failed (after skip-list)
    if errormux-skip-check "$_ERRORMUX_LAST_CMD" "$_ERRORMUX_LAST_EXIT"; then
        return
    fi
    
    # Invoke Python CLI with captured state
    errormux-cli explain \
        --command "$_ERRORMUX_LAST_CMD" \
        --exit-code "$_ERRORMUX_LAST_EXIT" \
        --stderr "$_ERRORMUX_LAST_STDERR"
}

zle -N errormux-explain errormux_explain
bindkey '??' errormux-explain
```

### Pattern 3: Cache-First Lookup

**What:** Check SQLite cache before calling Ollama. Use SHA256(command + exit_code) as key.

**When to use:** When LLM calls are slow (1-5s) and expensive, but explanations for same errors are reusable.

**Trade-offs:**
- ✅ Sub-100ms responses for cached queries
- ✅ Reduces Ollama load significantly
- ❌ Cache invalidation complexity (TTL vs manual)
- ❌ Storage growth over time (need cleanup)

**Example:**
```python
# In cache.py
import hashlib
import sqlite3
from datetime import datetime, timedelta

def get_cache_key(command: str, exit_code: int) -> str:
    return hashlib.sha256(f"{command}:{exit_code}".encode()).hexdigest()

def lookup(command: str, exit_code: int, ttl_days: int = 7) -> Optional[dict]:
    key = get_cache_key(command, exit_code)
    conn = sqlite3.connect(CACHE_PATH)
    cursor = conn.execute(
        "SELECT why, fix, created_at FROM cache WHERE key = ?",
        (key,)
    )
    row = cursor.fetchone()
    if row:
        created = datetime.fromisoformat(row[2])
        if datetime.now() - created < timedelta(days=ttl_days):
            return {"why": row[0], "fix": row[1]}
    return None
```

### Pattern 4: Stderr Capture via Temp File

**What:** Redirect stderr to a temp file in preexec, read in precmd, clean up.

**When to use:** When you need actual error output, not just exit codes.

**Trade-offs:**
- ✅ Captures actual error messages
- ✅ Works for any command
- ❌ Temp file management overhead
- ❌ May interfere with commands that check stderr

**Example:**
```zsh
_ERRORMUX_STDERR_FILE="/tmp/errormux-stderr-$$.txt"

errormux_preexec() {
    _ERRORMUX_LAST_CMD="$1"
    # Redirect stderr to temp file while preserving stdout
    exec 2> >(tee "$_ERRORMUX_STDERR_FILE" >&2)
}

errormux_precmd() {
    _ERRORMUX_LAST_EXIT=$?
    # Read captured stderr
    _ERRORMUX_LAST_STDERR=$(cat "$_ERRORMUX_STDERR_FILE" 2>/dev/null || echo "")
    # Truncate for next command
    : > "$_ERRORMUX_STDERR_FILE"
}
```

## Data Flow

### Request Flow (User types `??`)

```
User types `??`
    ↓
zle widget triggered
    ↓
Check skip-list (zsh function)
    ↓ (not skipped)
Invoke Python CLI: errormux-cli explain --command "..." --exit-code N --stderr "..."
    ↓
Python: Check cache (SHA256 lookup)
    ↓ (cache miss)
Python: Build prompt (command + exit_code + stderr)
    ↓
Python: Call Ollama API (POST /api/generate, stream=True)
    ↓
Python: Parse streaming response (WHY/FIX structure)
    ↓
Python: Store in cache
    ↓
Python: Format output with Rich (streamed)
    ↓
Output displayed to user
```

### State Capture Flow (Every Command)

```
User hits Enter on command
    ↓
preexec hook fires
    ↓
Store command in _ERRORMUX_LAST_CMD
    ↓
Set up stderr redirection
    ↓
Command executes
    ↓
precmd hook fires
    ↓
Store $? in _ERRORMUX_LAST_EXIT
    ↓
Read stderr from temp file into _ERRORMUX_LAST_STDERR
    ↓
User sees prompt, hooks done
```

### Key Data Flows

1. **Command context flow:** preexec captures → global vars → widget reads → passes to CLI
2. **Cache lookup flow:** CLI receives → hash command+exit → SQLite query → return or continue
3. **LLM response flow:** Ollama streams → httpx chunks → Rich live display → stdout
4. **Install flow:** install.sh → check deps → clone plugin → pip install → source .zshrc

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Single user | Current architecture is optimal |
| Multiple users on same machine | Move cache to per-user XDG_DATA_HOME |
| Shared team cache | Add HTTP cache server, but unlikely needed |

### Scaling Priorities

1. **First bottleneck:** Ollama response latency (1-5s)
   - Fix: Cache is primary mitigation, accept latency for cache misses
   
2. **Second bottleneck:** Cache database size
   - Fix: Implement TTL cleanup on every Nth lookup, or cron job

## Anti-Patterns

### Anti-Pattern 1: Capturing stderr in precmd

**What people do:** Try to read stderr in precmd hook without preexec setup

**Why it's wrong:** By the time precmd runs, stderr has already been consumed by the shell. The file descriptor state from preexec is needed.

**Do this instead:** Set up stderr redirection in preexec, read in precmd.

### Anti-Pattern 2: Blocking preexec with slow operations

**What people do:** Run expensive checks in preexec hook

**Why it's wrong:** preexec blocks the shell prompt. Even 100ms delay is noticeable.

**Do this instead:** Keep preexec minimal (just state capture). Do heavy work in widget (on-demand).

### Anti-Pattern 3: Widget name collisions

**What people do:** Name widgets generically like `explain` or `show_error`

**Why it's wrong:** Other plugins may define same widget, causing conflicts

**Do this instead:** Namespace all widgets (e.g., `_errormux_explain`, `errormux-explain`)

### Anti-Pattern 4: Cache key without exit code

**What people do:** Hash only command text for cache key

**Why it's wrong:** Same command can fail for different reasons (different exit codes, different errors)

**Do this instead:** Include exit code in hash: `SHA256(command + ":" + exit_code)`

### Anti-Pattern 5: Hardcoded Ollama URL

**What people do:** Assume Ollama runs at localhost:11434

**Why it's wrong:** Users may run Ollama on different host/port, or use remote API

**Do this instead:** Read from config.toml or environment variable (`OLLAMA_HOST`)

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Ollama | HTTP REST API (httpx) | localhost:11434, `/api/generate` endpoint |
| SQLite | File-based DB (sqlite3) | Single table, no migrations needed |
| zsh | Hook system + zle widgets | `add-zsh-hook`, `zle -N`, `bindkey` |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| zsh plugin ↔ Python CLI | subprocess invocation | Pass state via CLI args |
| Python CLI ↔ Cache | Direct function calls | Same process, fast |
| Python CLI ↔ Ollama | HTTP async (httpx) | Streaming response |

## Sources

- zsh documentation on hook functions: https://zsh.sourceforge.io/Doc/Release/Functions.html
- zsh-autosuggestions source (reference implementation): https://github.com/zsh-users/zsh-autosuggestions
- thefuck shell integration pattern: https://github.com/nvbn/thefuck
- zoxide init pattern: https://github.com/ajeetdsouza/zoxide
- Oh My Zsh plugin standard: https://github.com/ohmyzsh/ohmyzsh

---
*Architecture research for: zsh plugin + Python backend (ErrorMux)*
*Researched: 2026-04-15*
