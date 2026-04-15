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

- [ ] **CLI-01**: Read three tmp files (cmd, stderr, exit code)
- [ ] **CLI-02**: SHA256(cmd+stderr) → SQLite cache at ~/.shell-explainer/cache.db
- [ ] **CLI-03**: Return cached explanation instantly on cache hit
- [ ] **CLI-04**: On miss: POST to Ollama /api/generate with structured prompt
- [ ] **CLI-05**: Stream output to stdout with Rich (dim gray WHY, bold green FIX)
- [ ] **CLI-06**: 10s timeout; on failure print "[explainer offline]" and exit 0

### Skip-List

- [ ] **SKIP-01**: Filter out grep exit 1 (no match, not error)
- [ ] **SKIP-02**: Filter out test/[[ exit 1 (condition false, not error)
- [ ] **SKIP-03**: Filter out diff exit 1 (files differ, not error)
- [ ] **SKIP-04**: Configurable patterns in ~/.shell-explainer/config.toml

### Installation

- [ ] **INST-01**: install.sh copies plugin to ~/.config/shell-explainer/
- [ ] **INST-02**: install.sh appends source line to .zshrc if missing
- [ ] **INST-03**: install.sh installs Python deps via uv

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
| (Populated during roadmap creation) | | |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 0
- Unmapped: 15 ⚠️

---
*Requirements defined: 2026-04-15*
*Last updated: 2026-04-15 after initial definition*
