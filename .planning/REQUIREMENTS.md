# Requirements: ErrorMux

**Defined:** 2026-04-16
**Core Value:** Fast, local, on-demand error explanations that don't interrupt your flow — only when you ask for them.

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Configuration

- **CFG-01**: User can configure model name via config file
- **CFG-02**: User can configure cache TTL via config file
- **CFG-03**: User can configure keybinding via config file

### Advanced Features

- **ADV-01**: User can request multi-line explanations
- **ADV-02**: User can copy fix command to clipboard

### GitHub

- **CI-01**: GitHub Actions CI workflow for automated testing
- **CI-02**: Coverage badge shows real coverage percentage

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Auto-printing on every error | Opt-in via `??` only is core value |
| Cloud fallback or remote LLM APIs | Offline-first is core value |
| Multi-shell support (bash/fish) | zsh-specific hooks are core to design |
| GUI or TUI | Single ?? output is core design |

---

*Requirements defined: 2026-04-16*
*Last updated: 2026-04-16 after v1.1 milestone completion*
*v1.0 and v1.1 requirements archived to milestones/*
