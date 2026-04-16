# Roadmap: ErrorMux

## Milestones

- ✅ **v1.0 MVP** — Phases 1-6 (shipped 2026-04-16)
- 🚧 **v1.1 Polish & Package** — Phases 7-10 (in progress)

## Overview

ErrorMux v1.1 fixes the widget UX (auto-return to prompt), switches to gemma4:e2b model, packages for multiple installation methods (Oh My Zsh, curl, manual), and polishes the GitHub repository with complete documentation, LICENSE, badges, and demo GIF.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

<details>
<summary>✅ v1.0 MVP (Phases 1-6) — SHIPPED 2026-04-16</summary>

- [x] Phase 1: Capture Layer (2/2 plans) — zsh hooks capture command context
- [x] Phase 2: CLI + Ollama Core (2/2 plans) — Python CLI with streaming output
- [x] Phase 3: Cache System (2/2 plans) — SQLite cache with 7-day TTL
- [x] Phase 4: Skip-List Filtering (2/2 plans) — Filter false-positive errors
- [x] Phase 5: Installation (2/2 plans) — One-command installer
- [x] Phase 6: Testing (2/2 plans) — pytest-cov with 92% coverage

</details>

### 🚧 v1.1 Polish & Package (In Progress)

**Milestone Goal:** Fix UX issues, switch to Gemma 4, package for public distribution, and publish to GitHub.

- [ ] **Phase 7: Widget Auto-Return Fix** — Clean prompt return after ?? output
- [ ] **Phase 8: Model Switch** — Use gemma4:e2b with proper cache handling
- [ ] **Phase 9: Packaging** — Multiple install methods (Oh My Zsh, curl, manual)
- [ ] **Phase 10: GitHub Polish** — README, LICENSE, badges, demo GIF

## Phase Details

### Phase 7: Widget Auto-Return Fix
**Goal**: User's shell prompt auto-returns cleanly after ?? output displays
**Depends on**: Phase 6 (v1.0 complete)
**Requirements**: WUX-01, WUX-02
**Success Criteria** (what must be TRUE):
  1. User can press ?? and see output without needing to press Enter afterward
  2. Prompt returns to ready state automatically after output displays
  3. Widget exits cleanly without requiring Ctrl+C or manual intervention
**Plans**: 2 plans
- [ ] 07-01-PLAN.md — Widget ZLE reset implementation
- [ ] 07-02-PLAN.md — Interactive UX verification

### Phase 8: Model Switch
**Goal**: Plugin uses gemma4:e2b model with proper cache handling
**Depends on**: Phase 7
**Requirements**: MODL-01, MODL-02, MODL-03
**Success Criteria** (what must be TRUE):
  1. Plugin calls gemma4:e2b model via Ollama for all explanations
  2. Cache keys include model name to prevent stale explanations after model switch
  3. Config file documents model requirement so users know to pull gemma4:e2b
**Plans**: TBD

### Phase 9: Packaging
**Goal**: Users can install via multiple documented methods
**Depends on**: Phase 8
**Requirements**: PKG-01, PKG-02, PKG-03, PKG-04, PKG-05
**Success Criteria** (what must be TRUE):
  1. User can install via Oh My Zsh by cloning to $ZSH_CUSTOM/plugins/errormux/
  2. User can install via one-line curl command
  3. User can install manually with documented git clone + .zshrc steps
  4. install.sh script detects Oh My Zsh automatically and uses correct path
**Plans**: TBD

### Phase 10: GitHub Polish
**Goal**: Professional GitHub presence with complete documentation
**Depends on**: Phase 9
**Requirements**: GH-01, GH-02, GH-03, GH-04, GH-05, GH-06, GH-07, GH-08
**Success Criteria** (what must be TRUE):
  1. README shows usage with command examples
  2. README shows installation instructions for all three methods
  3. MIT LICENSE file exists in repo root
  4. README header shows test coverage badge
  5. README header shows license badge
  6. Demo GIF shows plugin workflow (failed command → ?? → explanation → clean prompt)
  7. Repo is pushed to github.com/kartikparsoya-eng/ErrorMux
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 7 → 8 → 9 → 10

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Capture Layer | v1.0 | 2/2 | Complete | 2026-04-15 |
| 2. CLI + Ollama Core | v1.0 | 2/2 | Complete | 2026-04-15 |
| 3. Cache System | v1.0 | 2/2 | Complete | 2026-04-15 |
| 4. Skip-List Filtering | v1.0 | 2/2 | Complete | 2026-04-15 |
| 5. Installation | v1.0 | 2/2 | Complete | 2026-04-15 |
| 6. Testing | v1.0 | 2/2 | Complete | 2026-04-16 |
| 7. Widget Auto-Return Fix | v1.1 | 0/2 | Not started | - |
| 8. Model Switch | v1.1 | 0/TBD | Not started | - |
| 9. Packaging | v1.1 | 0/TBD | Not started | - |
| 10. GitHub Polish | v1.1 | 0/TBD | Not started | - |

---
*Roadmap created: 2026-04-15*
*Last updated: 2026-04-16 after roadmap creation for v1.1*
