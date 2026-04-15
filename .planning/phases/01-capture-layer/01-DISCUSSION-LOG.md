# Phase 1: Capture Layer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-15T10:20:00Z
**Phase:** 01-capture-layer
**Areas discussed:** Stderr capture method, Widget scope

---

## Stderr Capture Method

| Option | Description | Selected |
|--------|-------------|----------|
| Temp file redirect (Recommended) | Reliable, explicit file handle. Works with all commands including those that background. Slightly more setup in preexec. | ✓ |
| Process substitution | Cleaner syntax, streams to file. Edge cases with background jobs and some interactive commands. | |
| DEBUG trap | Most powerful, can capture stdout+stderr. Higher complexity, may conflict with other traps. | |

**User's choice:** Temp file redirect (Recommended)
**Notes:** User selected recommended option for reliability.

---

## Tee Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, tee to both (Recommended) | User sees errors in real-time as normal. File also captures for ?? later. | ✓ |
| No, redirect only | Silent capture only. Errors still go to terminal via original stream, but not tee'd. Simpler but may miss some output. | |

**User's choice:** Yes, tee to both (Recommended)
**Notes:** Errors visible in terminal AND captured for later explanation.

---

## Widget Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Stub CLI in Phase 1 (Recommended) | Widget in Phase 1 calls a stub CLI (just prints 'CLI not implemented'). Real CLI in Phase 2. | ✓ |
| Defer widget to Phase 2 | Widget defined in Phase 2 after CLI works. Phase 1 just captures data via hooks. | |

**User's choice:** Stub CLI in Phase 1 (Recommended)
**Notes:** Widget defined now with placeholder, real implementation in Phase 2.

---

## Claude's Discretion

Areas where user deferred to Claude:
- Hook registration pattern (preexec_functions vs direct function)
- Plugin file structure (single file vs multiple)
- Exact stderr redirect implementation mechanism

---

## Deferred Ideas

None — discussion stayed within phase scope.
