---
phase: 02
slug: cli-ollama-core
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-04-15"
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `pyproject.toml` (tool.pytest) |
| **Quick run command** | `uv run pytest tests/ -x -q` |
| **Full suite command** | `uv run pytest tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest tests/ -x -q`
- **After every plan wave:** Run `uv run pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | CLI-01 | T-02-02 | Read temp files safely, no execution | unit | `uv run pytest tests/test_cli.py::test_read_context -xvs` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | CLI-04 | T-02-01 | Call Ollama with timeout, no shell eval | unit | `uv run pytest tests/test_ollama_client.py::test_chat_timeout -xvs` | ❌ W0 | ⬜ pending |
| 02-01-03 | 01 | 1 | CLI-05 | N/A | Print WHY/FIX with Rich, no clipboard | unit | `uv run pytest tests/test_output.py::test_rich_formatting -xvs` | ❌ W0 | ⬜ pending |
| 02-01-04 | 01 | 1 | CLI-06 | N/A | Exit 0 on all failures, no exceptions | unit | `uv run pytest tests/test_error_handling.py::test_timeout_exit_0 -xvs` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | CLI-04 | N/A | Full integration with mocked Ollama | integration | `uv run pytest tests/test_cli.py::test_explain_command -xvs` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_cli.py` — test read_context, explain command
- [ ] `tests/test_ollama_client.py` — test Ollama client wrapper
- [ ] `tests/test_output.py` — test response parsing and Rich formatting
- [ ] `tests/test_error_handling.py` — test timeout, service down, parse failure
- [ ] `tests/conftest.py` — shared fixtures (mock client, temp files)

*Existing pytest infrastructure from Phase 1 (pyproject.toml has pytest>=8.0)*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| E2E with real Ollama | CLI-04 | Requires running Ollama service | 1. Start Ollama: `ollama serve` 2. Pull model: `ollama pull gemma3:4b` 3. Source plugin 4. Run failing command 5. Type `??` 6. Verify output appears |

*Primary behaviors have automated verification via mocking. E2E with real service is optional integration test.*

---

## Test Doubles Strategy

### Mocking Ollama Client

```python
# tests/conftest.py
from unittest.mock import MagicMock, patch
import pytest

@pytest.fixture
def mock_ollama_client():
    """Mock ollama.Client for unit tests."""
    with patch('ollama.Client') as mock:
        yield mock

@pytest.fixture
def mock_temp_files(tmp_path):
    """Create temp files for testing."""
    cmd_file = tmp_path / "shell-explainer-last-cmd"
    stderr_file = tmp_path / "shell-explainer-last-stderr"
    exit_file = tmp_path / "shell-explainer-last-exit"
    
    cmd_file.write_text("ls nonexistent")
    stderr_file.write_text("No such file or directory")
    exit_file.write_text("2")
    
    return {
        'cmd': cmd_file,
        'stderr': stderr_file,
        'exit': exit_file
    }
```

### Mocking Rich Console

```python
@pytest.fixture
def mock_console():
    """Capture Rich console output."""
    from rich.console import Console
    from io import StringIO
    
    console = Console(file=StringIO(), force_terminal=True)
    return console
```

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
