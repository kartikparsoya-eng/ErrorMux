# Phase 6: Testing - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-15
**Phase:** 06-testing
**Areas discussed:** Coverage target, TEST-04 compliance, Coverage tooling

---

## Coverage Target

| Option | Description | Selected |
|--------|-------------|----------|
| 80% | Standard industry threshold, allows for edge cases and error paths that are hard to test | ✓ |
| 90% | Higher bar, catches more regressions, some overhead for maintenance | |
| 100% | Maximum coverage, but pytest-cov only measures line coverage (not branch quality), and can be brittle | |

**User's choice:** 80%
**Notes:** Standard industry threshold appropriate for MVP. Allows for hard-to-test edge cases while ensuring core paths verified.

---

## TEST-04 Compliance

| Option | Description | Selected |
|--------|-------------|----------|
| Keep current approach | Tests work (63 passed), unittest.mock is simpler, no extra dependency | |
| Switch to httpx MockTransport | Strict compliance with TEST-04, tests real httpx transport layer, but adds complexity | ✓ |

**User's choice:** Switch to httpx MockTransport
**Notes:** Strict compliance with REQUIREMENTS.md TEST-04 specification. Tests will verify actual httpx transport layer behavior.

---

## Coverage Tooling

| Option | Description | Selected |
|--------|-------------|----------|
| Yes, add pytest-cov | Enables coverage reports, CI integration, and enforces target threshold | ✓ |
| No, skip for MVP | Tests exist and pass; coverage tooling can be added later if needed | |

**User's choice:** Yes, add pytest-cov
**Notes:** Enables coverage measurement and enforcement. Can integrate with CI for automated checks.

---

## Claude's Discretion

- Exact coverage report format (terminal, HTML, or both)
- Whether to fail CI on coverage threshold miss
- Test organization (per-module files vs unified test files)
- Handling of untestable code paths (e.g., zsh integration)

## Deferred Ideas

None — discussion stayed within phase scope.
