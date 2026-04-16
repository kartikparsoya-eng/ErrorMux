# Roadmap: ErrorMux

## Milestones

- ✅ **v1.0 MVP** — Phases 1-6 (shipped 2026-04-16)
- ✅ **v1.1 Polish & Package** — Phases 7-10 (shipped 2026-04-16)

## Overview

ErrorMux is a zsh plugin that explains shell command failures on-demand. Both MVP and Polish milestones are complete. The plugin is published at https://github.com/kartikparsoya-eng/ErrorMux.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

<details>
<summary>✅ v1.0 MVP (Phases 1-6) — SHIPPED 2026-04-16</summary>

- [x] Phase 1: Capture Layer (2/2 plans) — zsh hooks capture command context
- [x] Phase 2: CLI + Ollama Core (2/2 plans) — Python CLI with streaming output
- [x] Phase 3: Cache System (2/2 plans) — SQLite cache with 7-day TTL
- [x] Phase 4: Skip-List Filtering (2/2 plans) — Filter false-positive errors
- [x] Phase 5: Installation (2/2 plans) — One-command installer
- [x] Phase 6: Testing (2/2 plans) — pytest-cov with 92% coverage

</details>

<details>
<summary>✅ v1.1 Polish & Package (Phases 7-10) — SHIPPED 2026-04-16</summary>

- [x] Phase 7: Widget Auto-Return Fix (2/2 plans) — ZLE reset pattern for clean prompt return
- [x] Phase 8: Model Switch (2/2 plans) — gemma4:e2b with model-scoped cache keys
- [x] Phase 9: Packaging (3/3 plans) — Multi-method installation (Oh My Zsh, curl, manual)
- [x] Phase 10: GitHub Polish (4/4 plans) — LICENSE, badges, README, GitHub release

</details>

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Capture Layer | v1.0 | 2/2 | Complete | 2026-04-15 |
| 2. CLI + Ollama Core | v1.0 | 2/2 | Complete | 2026-04-15 |
| 3. Cache System | v1.0 | 2/2 | Complete | 2026-04-15 |
| 4. Skip-List Filtering | v1.0 | 2/2 | Complete | 2026-04-15 |
| 5. Installation | v1.0 | 2/2 | Complete | 2026-04-15 |
| 6. Testing | v1.0 | 2/2 | Complete | 2026-04-16 |
| 7. Widget Auto-Return Fix | v1.1 | 2/2 | Complete | 2026-04-16 |
| 8. Model Switch | v1.1 | 2/2 | Complete | 2026-04-16 |
| 9. Packaging | v1.1 | 3/3 | Complete | 2026-04-16 |
| 10. GitHub Polish | v1.1 | 4/4 | Complete | 2026-04-16 |

---

*Roadmap created: 2026-04-15*
*Last updated: 2026-04-16 after v1.1 milestone completion*
