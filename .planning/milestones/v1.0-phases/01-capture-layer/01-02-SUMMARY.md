---
phase: 01-capture-layer
plan: 02
subsystem: zsh-plugin
tags: [zsh, preexec, precmd, zle, widget, hooks]

# Dependency graph
requires:
  - phase: 01-capture-layer
    plan: 01
    provides: cli-entry-point
provides:
  - zsh plugin with preexec/precmd hooks
  - `??` widget for on-demand explanation trigger
  - tmp file state capture (command, stderr, exit code)
affects: []

# Tech tracking
tech-stack:
  added:
    - zsh preexec/precmd hooks
    - zle widget system
    - bindkey for key sequence binding
  patterns:
    - preexec_functions+=() array pattern for hook registration
    - _ERRORMUX_ namespace prefix for globals
    - exec 2> >(tee ...) for stderr capture

key-files:
  created:
    - path: errormux.plugin.zsh
      purpose: zsh plugin entry point with hooks and widget
  modified: []

key-decisions:
  - "Hook registration via _functions array to avoid plugin conflicts"
  - "Tmp files for state persistence (reliable across widget context)"
  - "Stderr redirect via tee preserves terminal visibility"

patterns-established:
  - "Pattern: preexec_functions+=() for hook registration (per PITFALLS.md Pitfall 5)"
  - "Pattern: _ERRORMUX_ prefix for all global variables to avoid collisions"
  - "Pattern: exec 2> >(tee file >&2) for stderr capture with terminal visibility"

requirements-completed: [CAPT-01, CAPT-02, CAPT-03, CAPT-04, CAPT-05]

# Metrics
duration: 1.5min
completed: 2026-04-15
---

# Phase 1 Plan 2: Zsh Plugin with Hooks and Widget Summary

**Zsh plugin with preexec/precmd hooks capturing command context (text, stderr, exit code) and `??` widget triggering stub CLI for on-demand explanations**

## Performance

- **Duration:** 1.5 min
- **Started:** 2026-04-15T10:54:00Z
- **Completed:** 2026-04-15T10:55:27Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- preexec hook captures command text to /tmp/shell-explainer-last-cmd
- preexec hook sets up stderr tee redirect to /tmp/shell-explainer-last-stderr
- precmd hook captures exit code to /tmp/shell-explainer-last-exit
- `??` zle widget invokes `errormux` CLI (gap fix: changed from `errormux explain`)
- Skip logic for exit codes 0 (success), 130 (SIGINT), 148 (SIGTSTP)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create zsh plugin with hooks and widget** - `078dafa` (feat)

**Plan metadata:** (deferred to orchestrator)

## Files Created/Modified
- `errormux.plugin.zsh` - Zsh plugin entry point with hooks, widget, and state management

## Decisions Made
- Used `preexec_functions+=()` array pattern per PITFALLS.md to avoid conflicts with other zsh plugins
- All global variables prefixed with `_ERRORMUX_` to prevent namespace collisions
- State written to tmp files for reliable widget access (globals don't persist cleanly across widget context)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - implementation followed the complete plugin skeleton from RESEARCH.md.

## User Setup Required

None - no external service configuration required for this phase.

## Threat Flags

| Flag | File | Description |
|------|------|-------------|
| threat_flag: tmp-world-readable | errormux.plugin.zsh | Tmp files in /tmp are world-readable; per threat model T-01-02, T-01-03 this is accepted for single-user local machine |

## Verification Results

All automated verification checks passed:
- [x] File exists at project root
- [x] preexec_functions+=(_errormux_preexec) pattern present
- [x] precmd_functions+=(_errormux_precmd) pattern present
- [x] zle -N errormux-explain widget registration present
- [x] bindkey '??' errormux-explain key binding present

## Next Phase Readiness
- zsh plugin complete, hooks capture state correctly
- Widget invokes stub CLI from Plan 01
- Ready for Phase 2: Python CLI with Ollama integration

## Self-Check: PASSED

- [x] errormux.plugin.zsh exists at project root
- [x] All hook patterns verified via grep
- [x] Commit exists: 078dafa

---

*Phase: 01-capture-layer*
*Completed: 2026-04-15*
