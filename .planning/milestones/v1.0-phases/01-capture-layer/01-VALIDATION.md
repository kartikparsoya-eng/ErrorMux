---
phase: 01
slug: capture-layer
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-15
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual zsh testing (no automated framework for zsh hooks) |
| **Config file** | none — manual verification |
| **Quick run command** | `source errormux.plugin.zsh && echo test` |
| **Full suite command** | Manual test sequence (see below) |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Manual verification in test shell
- **After every plan wave:** Full manual test sequence
- **Before `/gsd-verify-work`:** All manual tests must pass
- **Max feedback latency:** 30 seconds (manual)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | CAPT-04 | — | N/A | unit | `test -f pyproject.toml` | ✅ W1 | ⬜ pending |
| 01-01-02 | 01 | 1 | CAPT-04 | — | N/A | unit | `errormux explain --help` | ✅ W1 | ⬜ pending |
| 01-02-01 | 02 | 2 | CAPT-01-05 | — | N/A | manual | See below | ✅ W2 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red*

---

## Wave 0 Requirements

- [x] Existing infrastructure covers all phase requirements.
- [x] Python project structure verified by task acceptance criteria
- [x] zsh plugin verified by task acceptance criteria

*Note: zsh hook testing requires interactive shell — automated pytest cannot test preexec/precmd hooks directly.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Command capture to temp file | CAPT-01 | preexec runs in shell context | `source errormux.plugin.zsh && cat /tmp/shell-explainer-last-cmd` |
| Stderr tee to temp file | CAPT-02 | stderr redirection requires shell execution | `ls /nonexistent && cat /tmp/shell-explainer-last-stderr` |
| Exit code recording | CAPT-03 | precmd runs after command exits | `false && cat /tmp/shell-explainer-last-exit` |
| Widget invocation | CAPT-04 | zle widget requires interactive shell | Type `??` after a failed command |
| Skip codes (0, 130, 148) | CAPT-05 | Signal handling requires interactive shell | `true && cat /tmp/shell-explainer-last-exit` (should show 0, no explanation triggered) |

---

## Manual Test Sequence

Run these in a new zsh shell after sourcing the plugin:

```bash
# 1. Source the plugin
source errormux.plugin.zsh

# 2. Test command capture
echo "hello"
cat /tmp/shell-explainer-last-cmd
# Expected: echo "hello"

# 3. Test stderr capture
ls /nonexistent 2>&1
cat /tmp/shell-explainer-last-stderr
# Expected: ls: /nonexistent: No such file or directory

# 4. Test exit code capture
false
cat /tmp/shell-explainer-last-exit
# Expected: 1

# 5. Test skip code 0
true
cat /tmp/shell-explainer-last-exit
# Expected: 0

# 6. Test widget (should print placeholder)
ls /nonexistent
??
# Expected: "CLI not implemented yet - coming in Phase 2"
```

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s (manual)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
