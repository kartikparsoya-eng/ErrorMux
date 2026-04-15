# Feature Research

**Domain:** Shell error explanation/assistance tools
**Researched:** 2026-04-15
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Command capture** | Users expect the tool to know what command failed | LOW | Standard shell hooks (preexec/precmd) |
| **Exit code awareness** | Essential to know command failed | LOW | Built into shell |
| **Stderr capture** | Error messages are the primary diagnostic | MEDIUM | Requires careful hook implementation |
| **On-demand trigger** | Users don't want noise on every command | LOW | Simple keybinding |
| **Fast response** | Delays kill workflow | MEDIUM | Sub-second for cached, <10s for fresh |
| **No configuration required** | Install and go | MEDIUM | Sensible defaults are essential |
| **Offline capability** | Developers work offline often | HIGH | Local model or cached responses |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Local LLM (offline-first)** | Works without internet, no API costs, privacy | HIGH | ErrorMux's core differentiator |
| **Cache-backed speed** | Instant response for repeated errors | MEDIUM | SQLite with TTL |
| **Structured output (WHY + FIX)** | Clear, actionable information | LOW | Prompt engineering |
| **Skip-list for false positives** | Avoids noise from grep exit 1, test failures | MEDIUM | Critical for UX |
| **One-sentence explanation** | Quick comprehension without verbosity | LOW | Prompt constraint |
| **Zero cloud dependency** | Privacy, no tracking, works anywhere | LOW | Architecture decision |
| **Shell-agnostic hook system** | Works on zsh, bash, fish | MEDIUM | ErrorMux is zsh-only (intentional scope) |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Auto-print on every error** | "Why do I have to type `??`?" | Noisy, breaks flow, false positives from grep/diff/test | On-demand trigger (`??`) |
| **Cloud LLM fallback** | "Better explanations with GPT-4" | Privacy concern, API costs, latency, offline dependency | Local model only |
| **Multi-shell support** | "I use bash sometimes" | Dilutes core experience, zsh-specific hooks are superior | Focus on zsh, excellent zsh experience |
| **Rich TUI for explanations** | "More information, better UI" | Slows response, over-engineering for MVP | One-line WHY + one-line FIX |
| **Command execution from tool** | "Auto-fix and run" | Dangerous, bypasses user review | Show fix, let user run |
| **Learning mode (teaching correct fixes)** | "Get smarter over time" | Complex, adds state, potential for bad feedback loops | Simple cache with TTL |

## Feature Dependencies

```
Command Capture (preexec/precmd hooks)
    └──requires──> Shell Plugin Infrastructure
                       
Cache System (SQLite)
    └──requires──> Command Capture (for cache key)
                       
LLM Integration (Ollama)
    └──requires──> Command Capture + Stderr
                       
Structured Output (WHY/FIX)
    └──requires──> LLM Integration + Prompt Engineering
                       
Skip-list
    └──requires──> Command Capture + Exit Code
                       
`??` Widget
    └──requires──> All of the above
```

### Dependency Notes

- **Cache System requires Command Capture**: Cache key is SHA256 of command + stderr + exit code
- **Structured Output requires LLM Integration**: Prompt engineering shapes the response format
- **Skip-list requires Command Capture**: Need to know command and exit code to filter false positives
- **`??` Widget requires All**: This is the user-facing entry point that orchestrates everything

## MVP Definition

### Launch With (v1)

Minimum viable product — what's needed to validate the concept.

- [x] **zsh capture layer** — Hooks stderr, exit code, and command text for every interactive command
- [x] **`??` widget** — Reads captured data and invokes Python CLI
- [x] **SQLite cache (7-day TTL)** — Fast response for repeated errors
- [x] **Ollama integration** — Local gemma3:4b for WHY/FIX output
- [x] **Skip-list** — Filters grep exit 1, test/[[, diff exit 1
- [x] **Structured output (Rich)** — WHY (one sentence) + FIX (command)
- [x] **Install script** — Sets up plugin, Python deps, .zshrc sourcing

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **Config file (~/.shell-explainer/config.toml)** — User customization
- [ ] **Custom skip-list patterns** — User-defined false positives
- [ ] **Cache statistics** — Show cache hit rate, size
- [ ] **Verbose mode** — Longer explanations on demand
- [ ] **History integration** — Recall previous explanations

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Multi-model support** — Switch between gemma, llama, mistral
- [ ] **bash support** — If demand is significant
- [ ] **Explanation history browser** — TUI for past explanations
- [ ] **Context awareness** — Include git status, cwd context

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Command capture | HIGH | LOW | P1 |
| Exit code awareness | HIGH | LOW | P1 |
| Stderr capture | HIGH | MEDIUM | P1 |
| `??` widget | HIGH | LOW | P1 |
| Cache system | HIGH | MEDIUM | P1 |
| Skip-list | HIGH | MEDIUM | P1 |
| Local LLM | HIGH | MEDIUM | P1 |
| Structured output | HIGH | LOW | P1 |
| Config file | MEDIUM | LOW | P2 |
| Custom skip-list | MEDIUM | LOW | P2 |
| Cache stats | LOW | LOW | P3 |
| Verbose mode | MEDIUM | LOW | P2 |
| Multi-model | LOW | MEDIUM | P3 |
| bash support | LOW | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | thefuck (96.5k ⭐) | ai-shell (5.2k ⭐) | howto (104 ⭐) | ErrorMux (Our Approach) |
|---------|-------------------|--------------------|---------------|-------------------------|
| **Trigger** | Type `fuck` | Type `ai <prompt>` | ctrl+g | Type `??` |
| **Approach** | Rule-based | LLM (cloud) | LLM (cloud) | LLM (local) |
| **Offline** | ✅ Yes | ❌ No | ❌ No | ✅ Yes |
| **Error-focused** | ⚠️ Correction only | ❌ Command generation | ❌ General help | ✅ Yes (WHY + FIX) |
| **Explanation** | ❌ Just correction | ✅ Explains command | ⚠️ General help | ✅ WHY + FIX |
| **Cache** | ❌ No | ❌ No | ❌ No | ✅ Yes (7-day TTL) |
| **Skip false positives** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Privacy** | ✅ Local | ❌ Cloud API | ❌ Cloud API | ✅ Local |
| **Shell support** | Multi-shell | Any | Any | zsh only |

## Key Insights

### Table Stakes Analysis

1. **Command capture + error context** is the minimum bar. Every tool in this space captures command context. ErrorMux's approach using preexec/precmd hooks is standard.

2. **Fast response** is expected. thefuck's "instant mode" shows users won't tolerate delays. ErrorMux's cache-first architecture directly addresses this.

3. **Offline capability** is a gap in the market. Every LLM-based tool requires cloud APIs. This is ErrorMux's primary differentiator.

### Differentiator Analysis

1. **Local LLM + offline-first** is unmatched. No other tool offers local LLM explanation. This is the competitive moat.

2. **Cache-backed speed** is novel. Other tools re-query every time. ErrorMux's SQLite cache makes repeated errors instant.

3. **Skip-list for false positives** is unique. thefuck has no filtering, making it noisy for grep/diff/test failures.

### Anti-Feature Rationale

1. **Auto-print on every error** was explicitly rejected in PROJECT.md. On-demand (`??`) is the right choice — see thefuck's user feedback about noise.

2. **Cloud fallback** undermines the privacy/offline value proposition. Users who want cloud can use ai-shell or howto.

3. **Command execution** is dangerous. thefuck's confirmation step shows users want control. Show the fix, don't run it.

## Sources

- thefuck: https://github.com/nvbn/thefuck (96.5k stars) — Rule-based correction
- ai-shell: https://github.com/BuilderIO/ai-shell (5.2k stars) — LLM command generation
- howto: https://github.com/antonmedv/howto (104 stars) — LLM terminal helper
- shellcheck: https://github.com/koalaman/shellcheck (39.3k stars) — Static analysis
- atuin: https://github.com/atuinsh/atuin (29.2k stars) — Shell history
- explainshell: https://explainshell.com — Web-based command explanation
- Warp: https://www.warp.dev — Modern terminal with AI

---
*Feature research for: Shell error explanation tools*
*Researched: 2026-04-15*
