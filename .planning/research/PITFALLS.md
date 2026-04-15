# Domain Pitfalls

**Domain:** zsh plugin + local LLM integration
**Researched:** 2026-04-15
**Confidence:** MEDIUM (WebFetch sources from official docs, community FAQ, and Zsh manual; no Context7 verification available)

## Critical Pitfalls

### Pitfall 1: preexec/precmd Hook Race Condition

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

**Phase to address:**
Phase 1 (Capture Layer) — design the hook storage pattern explicitly

---

### Pitfall 2: Ollama Connection Timeout Blocks Shell

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

**Phase to address:**
Phase 2 (Python CLI) — implement timeout with proper error handling and user feedback

---

### Pitfall 3: Skip-List False Positives

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

**Phase to address:**
Phase 1 (Capture Layer) — define skip-list as a core component; Phase 4 (Skip-list) — implement fully

---

### Pitfall 4: Cache Poisoning via Similar Commands

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

**Phase to address:**
Phase 3 (Caching) — design cache key to include stderr and potentially cwd

---

### Pitfall 5: Hook Function Pollution Breaks Other Plugins

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

**Phase to address:**
Phase 1 (Capture Layer) — implement hook registration using `_functions` arrays

---

### Pitfall 6: Python Dependency Hell in Shell Context

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

**Phase to address:**
Phase 5 (Installation) — robust install script with dependency verification

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Skip caching, always call Ollama | Faster implementation, simpler code | Slow UX, Ollama overload, wasted tokens | Never — caching is core value |
| Hardcode gemma3:4b model name | No config complexity | Can't use different models, breaks if model renamed | Prototype only, replace before MVP |
| Ignore stderr, only look at exit code | Simpler prompt construction | Misses critical error context, poor explanations | Never |
| Synchronous-only (no background pre-fetch) | Simpler implementation | Cold Ollama = long first-call latency | MVP acceptable, improve later |

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Ollama HTTP API | Assume localhost:11434 always available | Check connectivity first, show helpful error if Ollama not running |
| Ollama streaming | Ignore stream mode, block on full response | Use `stream: false` for simplicity in MVP, but handle streaming for long responses |
| SQLite cache | Use single-threaded access, ignore concurrency | SQLite handles concurrent reads fine; serialize writes or use WAL mode |
| Zsh variables | Use global names like `LAST_CMD` that might conflict | Prefix all globals with `_ERRORMUX_` to avoid collisions |

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Unbounded cache growth | Cache.db grows to GB, slow lookups | Implement 7-day TTL cleanup (already planned); add size cap | Months of use without cleanup |
| Prompt too long | Ollama rejects request, or slow inference | Truncate command/stderr to reasonable length (e.g., 500 chars each) | User runs 1000-char piped command |
| Hook does heavy work | Shell lag on every command | Keep hooks minimal: only capture data, no processing until `??` called | Hooks contain network calls or file I/O |

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Include full stderr in prompt | Sensitive data (passwords, tokens, paths) sent to local LLM | Truncate stderr, warn user if using cloud models (but this project is local-only) |
| Execute commands from LLM output | LLM hallucinates dangerous commands, user blindly runs them | NEVER execute LLM suggestions. Only display them. Clearly mark as suggestions. |
| Store cache in world-readable location | Other users on shared machine see command history | Default cache path `~/.shell-explainer/cache.db` with mode 600 |

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Auto-explain on every error | Noisy, interrupts flow, user tunes out | Opt-in via `??` only (already specified) — respects user's workflow |
| Verbose output | Screen clutter, hard to parse | One-sentence WHY, one-sentence FIX, no fluff (already specified) |
| No feedback during Ollama call | User thinks it's broken | Show "Thinking..." spinner during inference |
| Explanation too technical | User doesn't understand "ENOENT" or "SIGSEGV" | Gemma prompt should request plain language, jargon-free explanations |

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **Hook capture:** Often missing stderr capture — verify `$ERRORMUX_LAST_STDERR` is set in precmd
- [ ] **Skip-list:** Often missing edge cases (e.g., `git diff`, `test -e`) — verify against real-world command corpus
- [ ] **Cache invalidation:** Often missing TTL enforcement — verify 7-day old entries are purged
- [ ] **Install script:** Often missing Python version check — verify `python3 --version` >= 3.12
- [ ] **Ollama connectivity:** Often missing graceful degradation — verify behavior when Ollama not running

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Hook race condition | LOW | Clear captured state after read; add timestamp validation |
| Ollama timeout | MEDIUM | Implement timeout + "Ollama slow" message; restart Ollama service |
| Skip-list false positive | MEDIUM | Add command to skip-list; update prompt to handle edge case |
| Cache poisoning | HIGH | Clear cache.db; redesign cache key to include more context |
| Hook pollution | HIGH | Switch to `_functions` array pattern; coordinate with other plugin maintainers |
| Dependency hell | MEDIUM | Re-run install script; check `uv pip list`; verify Python version |

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Hook race condition | Phase 1 | Unit test: fast command sequence + `??` shows correct state |
| Ollama timeout | Phase 2 | Integration test: kill Ollama, verify graceful error |
| Skip-list false positives | Phase 4 | Test corpus: 50+ common commands with non-error exit codes |
| Cache poisoning | Phase 3 | Test: same command, different stderr, different explanations |
| Hook pollution | Phase 1 | Test: load ErrorMux + other plugin, verify both hooks work |
| Dependency hell | Phase 5 | Fresh VM install: verify one-command setup works |

## Sources

- Oh My Zsh FAQ: https://github.com/ohmyzsh/ohmyzsh/wiki/FAQ — Common zsh plugin issues (completion, locale, PATH)
- Zinit Documentation: https://github.com/zdharma-continuum/zinit — Plugin manager patterns, hook debugging
- Zsh Functions Manual: https://zsh.sourceforge.net/Doc/Release/Functions.html — Hook function arrays (preexec_functions, precmd_functions)
- Ollama API Documentation: https://github.com/ollama/ollama/blob/main/docs/api.md — Timeout handling, streaming, model loading
- Ollama Python Library: https://github.com/ollama/ollama-python — Error handling patterns, ResponseError
- Project Context: .planning/PROJECT.md — ErrorMux architecture and constraints

---
*Pitfalls research for: zsh plugin + local LLM integration*
*Researched: 2026-04-15*
