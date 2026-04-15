# Requirements: ErrorMux

**Defined:** 2026-04-15
**Core Value:** Fast, local, on-demand error explanations that don't interrupt your flow — only when you ask for them.

## v1 Requirements

### Capture Layer

- [ ] **CAPT-01**: preexec hook captures command to /tmp/shell-explainer-last-cmd
- [ ] **CAPT-02**: preexec hook tees stderr to /tmp/shell-explainer-last-stderr
- [ ] **CAPT-03**: precmd hook records exit code to /tmp/shell-explainer-last-exit
- [ ] **CAPT-04**: `??` widget reads tmp files and invokes Python CLI
- [ ] **CAPT-05**: Skip explanation when exit code is 0, 130, or 148

### CLI Core

- [x] **CLI-01**: Read three tmp files (cmd, stderr, exit code)
- [ ] **CLI-02**: SHA256(cmd+stderr) → SQLite cache at ~/.shell-explainer/cache.db
- [ ] **CLI-03**: Return cached explanation instantly on cache hit
- [x] **CLI-04**: On miss: POST to Ollama /api/generate with structured prompt
- [x] **CLI-05**: Stream output to stdout with Rich (dim gray WHY, bold green FIX)
- [x] **CLI-06**: 10s timeout; on failure print "[explainer offline]" and exit 0

### Skip-List

- [x] **SKIP-01**: Filter out grep exit 1 (no match, not error)
- [x] **SKIP-02**: Filter out test/[[ exit 1 (condition false, not error)
- [x] **SKIP-03**: Filter out diff exit 1 (files differ, not error)
- [x] **SKIP-04**: Configurable patterns in ~/.shell-explainer/config.toml

### Installation

- [x] **INST-01**: install.sh copies plugin to ~/.config/shell-explainer/
- [x] **INST-02**: install.sh appends source line to .zshrc if missing
- [x] **INST-03**: install.sh installs Python deps via uv

### Testing

- [ ] **TEST-01**: pytest for cache hit/miss logic
- [ ] **TEST-02**: pytest for skip-list filtering
- [ ] **TEST-03**: pytest for prompt construction
- [ ] **TEST-04**: Mock Ollama with httpx MockTransport

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Configuration

- **CONF-01**: Custom skip-list patterns beyond defaults
- **CONF-02**: Cache TTL configuration
- **CONF-03**: Verbose mode for longer explanations

### Quality of Life

- **QOL-01**: Cache statistics command
- **QOL-02**: History of past explanations
- **QOL-03**: Multi-model support (switch gemma/llama/mistral)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Auto-print on every error | Opt-in via `??` only — avoids noise |
| Cloud fallback | Offline-first, privacy-first design |
| Multi-shell support | zsh only — leverage zsh-specific hooks |
| Command execution from tool | Dangerous — show fix, let user run |
| GUI/TUI beyond `??` output | Over-engineering for MVP |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CAPT-01 | Phase 1 | Pending |
| CAPT-02 | Phase 1 | Pending |
| CAPT-03 | Phase 1 | Pending |
| CAPT-04 | Phase 1 | Pending |
| CAPT-05 | Phase 1 | Pending |
| CLI-01 | Phase 2 | Complete |
| CLI-02 | Phase 3 | Pending |
| CLI-03 | Phase 3 | Pending |
| CLI-04 | Phase 2 | Complete |
| CLI-05 | Phase 2 | Complete |
| CLI-06 | Phase 2 | Complete |
| SKIP-01 | Phase 4 | Complete |
| SKIP-02 | Phase 4 | Complete |
| SKIP-03 | Phase 4 | Complete |
| SKIP-04 | Phase 4 | Complete |
| INST-01 | Phase 5 | Complete |
| INST-02 | Phase 5 | Complete |
| INST-03 | Phase 5 | Complete |
| TEST-01 | Phase 6 | Pending |
| TEST-02 | Phase 6 | Pending |
| TEST-03 | Phase 6 | Pending |
| TEST-04 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-15*
*Last updated: 2026-04-15 after initial definition*
