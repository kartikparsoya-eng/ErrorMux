# Requirements: ErrorMux

**Defined:** 2026-04-16
**Core Value:** Fast, local, on-demand error explanations that don't interrupt your flow — only when you ask for them.

## v1.1 Requirements

Requirements for polish & packaging milestone.

### Widget UX

- [x] **WUX-01**: User's shell prompt auto-returns after `??` output displays
- [x] **WUX-02**: Widget exits cleanly without requiring manual keypress (Ctrl+X)

### Model Configuration

- [ ] **MODL-01**: Plugin uses gemma4:e2b model via Ollama
- [ ] **MODL-02**: Cache key includes model name to prevent stale explanations after model switch
- [ ] **MODL-03**: Config file documents model requirement for users

### Packaging

- [ ] **PKG-01**: User can install via Oh My Zsh (clone to `$ZSH_CUSTOM/plugins/errormux/`)
- [ ] **PKG-02**: User can install via one-line curl command
- [ ] **PKG-03**: User can install manually (git clone + .zshrc edit)
- [ ] **PKG-04**: install.sh detects Oh My Zsh and uses correct path
- [ ] **PKG-05**: All install methods documented in README

### GitHub Polish

- [ ] **GH-01**: README includes usage documentation with examples
- [ ] **GH-02**: README includes installation instructions for all methods
- [ ] **GH-03**: README includes configuration options
- [ ] **GH-04**: MIT LICENSE file exists in repo root
- [ ] **GH-05**: README header includes test coverage badge
- [ ] **GH-06**: README header includes license badge
- [ ] **GH-07**: Demo GIF shows plugin in action (failed command → ?? → explanation → clean prompt)
- [ ] **GH-08**: Repo pushed to github.com/kartikparsoya-eng/ErrorMux

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Configuration

- **CFG-01**: User can configure model name via config file
- **CFG-02**: User can configure cache TTL via config file
- **CFG-03**: User can configure keybinding via config file

### Advanced Features

- **ADV-01**: User can request multi-line explanations
- **ADV-02**: User can copy fix command to clipboard

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Auto-printing on every error | Opt-in via `??` only is core value |
| Cloud fallback or remote LLM APIs | Offline-first is core value |
| Multi-shell support (bash/fish) | zsh-specific hooks are core to design |
| GUI or TUI | Single ?? output is core design |
| GitHub Actions CI workflow | Deferred to v2 (requires repo setup first) |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| WUX-01 | Phase 7 | Complete |
| WUX-02 | Phase 7 | Complete |
| MODL-01 | Phase 8 | Pending |
| MODL-02 | Phase 8 | Pending |
| MODL-03 | Phase 8 | Pending |
| PKG-01 | Phase 9 | Pending |
| PKG-02 | Phase 9 | Pending |
| PKG-03 | Phase 9 | Pending |
| PKG-04 | Phase 9 | Pending |
| PKG-05 | Phase 9 | Pending |
| GH-01 | Phase 10 | Pending |
| GH-02 | Phase 10 | Pending |
| GH-03 | Phase 10 | Pending |
| GH-04 | Phase 10 | Pending |
| GH-05 | Phase 10 | Pending |
| GH-06 | Phase 10 | Pending |
| GH-07 | Phase 10 | Pending |
| GH-08 | Phase 10 | Pending |

**Coverage:**
- v1.1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-16*
*Last updated: 2026-04-16 after initial definition*
