# Roadmap: ErrorMux

## Overview

ErrorMux delivers fast, local, on-demand error explanations for shell commands. The journey starts with zsh capture hooks, builds the Python CLI with Ollama integration, adds caching for performance, implements skip-list filtering for quality, provides a single-command installer, and ends with comprehensive testing. Each phase delivers a verifiable capability that compounds on the previous.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Capture Layer** - zsh hooks capture command context for on-demand analysis
- [ ] **Phase 2: CLI + Ollama Core** - Python CLI calls local LLM and streams formatted explanations
- [ ] **Phase 3: Cache System** - SQLite cache delivers instant explanations for repeated errors
- [ ] **Phase 4: Skip-List Filtering** - Filter out false-positive "errors" like grep exit 1
- [ ] **Phase 5: Installation** - One-command setup with plugin, deps, and .zshrc integration
- [ ] **Phase 6: Testing** - pytest coverage for cache, skip-list, and prompt construction

## Phase Details

### Phase 1: Capture Layer
**Goal**: Shell correctly captures command context for analysis
**Depends on**: Nothing (first phase)
**Requirements**: CAPT-01, CAPT-02, CAPT-03, CAPT-04, CAPT-05
**Success Criteria** (what must be TRUE):
  1. User runs a command, and the command text is captured to /tmp/shell-explainer-last-cmd
  2. When a command runs, stderr is tee'd to /tmp/shell-explainer-last-stderr
  3. Exit code is recorded to /tmp/shell-explainer-last-exit after each command completes
  4. User can trigger `??` widget which reads temp files and invokes Python CLI
  5. Exit codes 0, 130, and 148 are skipped (no explanation triggered)
**Plans**: 2 plans

Plans:
- [x] 01-01-PLAN.md — Python project setup + stub CLI (Wave 1)
- [x] 01-02-PLAN.md — zsh plugin with hooks and widget (Wave 2)

### Phase 2: CLI + Ollama Core
**Goal**: Users receive AI-powered explanations for failed commands
**Depends on**: Phase 1
**Requirements**: CLI-01, CLI-04, CLI-05, CLI-06
**Success Criteria** (what must be TRUE):
  1. CLI reads captured command, stderr, and exit code from three temp files
  2. CLI calls Ollama localhost:11434 and receives structured WHY/FIX output
  3. Output streams to terminal with dim gray WHY and bold green FIX formatting via Rich
  4. On 10s timeout or failure, user sees "[explainer offline]" and CLI exits 0 gracefully
**Plans**: TBD

### Phase 3: Cache System
**Goal**: Repeated errors get instant explanations without LLM calls
**Depends on**: Phase 2
**Requirements**: CLI-02, CLI-03
**Success Criteria** (what must be TRUE):
  1. First occurrence of an error gets LLM explanation and is cached
  2. Same error repeated gets cached explanation instantly (sub-100ms response)
  3. Cache persists for 7 days with TTL enforcement
  4. Cache key includes SHA256(cmd+stderr) for accuracy (different stderr = different explanation)
**Plans**: TBD

### Phase 4: Skip-List Filtering
**Goal**: False-positive "errors" don't produce useless explanations
**Depends on**: Phase 2
**Requirements**: SKIP-01, SKIP-02, SKIP-03, SKIP-04
**Success Criteria** (what must be TRUE):
  1. grep exit 1 (no match, not error) doesn't trigger LLM explanation request
  2. test/[[ exit 1 (condition false, not error) doesn't trigger explanation
  3. diff exit 1 (files differ, not error) doesn't trigger explanation
  4. Users can configure additional skip patterns in ~/.shell-explainer/config.toml
**Plans**: TBD

### Phase 5: Installation
**Goal**: Users can install ErrorMux with a single command
**Depends on**: Phase 4
**Requirements**: INST-01, INST-02, INST-03
**Success Criteria** (what must be TRUE):
  1. Running install.sh copies plugin to ~/.config/shell-explainer/
  2. .zshrc is updated with source line if missing (no duplicate entries)
  3. Python dependencies (httpx, typer, rich) are installed via uv automatically
**Plans**: TBD

### Phase 6: Testing
**Goal**: All components are verified with automated tests
**Depends on**: Phase 5
**Requirements**: TEST-01, TEST-02, TEST-03, TEST-04
**Success Criteria** (what must be TRUE):
  1. Cache hit/miss logic is tested with pytest
  2. Skip-list filtering is tested with pytest
  3. Prompt construction is tested with pytest
  4. Ollama calls are mocked with httpx MockTransport and tested
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Capture Layer | 0/2 | Ready to execute | - |
| 2. CLI + Ollama Core | 0/TBD | Not started | - |
| 3. Cache System | 0/TBD | Not started | - |
| 4. Skip-List Filtering | 0/TBD | Not started | - |
| 5. Installation | 0/TBD | Not started | - |
| 6. Testing | 0/TBD | Not started | - |

---
*Roadmap created: 2026-04-15*
*Milestone: v1.0 MVP*
