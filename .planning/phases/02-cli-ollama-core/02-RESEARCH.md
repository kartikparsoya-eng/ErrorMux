# Phase 2: CLI + Ollama Core - Research

**Researched:** 2026-04-15
**Phase Goal:** Users receive AI-powered explanations for failed commands
**Requirements:** CLI-01, CLI-04, CLI-05, CLI-06

---

## Domain Overview

Phase 2 builds the core Python CLI that:
1. Reads captured command context from temp files (CLI-01)
2. Calls Ollama localhost:11434 for AI-powered explanations (CLI-04)
3. Streams formatted WHY/FIX output via Rich (CLI-05)
4. Handles timeout/failure gracefully (CLI-06)

---

## Standard Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| CLI Framework | typer | 0.15+ | Command-line interface |
| Terminal Output | rich | 14.0+ | Formatted output with colors |
| LLM Client | ollama | 0.6.1+ | Ollama Python SDK |
| Runtime | Python | 3.12+ | Main runtime |

**Already installed:** typer, rich (from Phase 1)
**Need to add:** ollama

---

## Architecture Patterns

### 1. Ollama Client Configuration

Per D-09 (single 10s timeout), use the ollama SDK's httpx kwargs:

```python
from ollama import Client

client = Client(host='http://localhost:11434', timeout=10.0)
```

**Why not AsyncClient:** Synchronous is simpler for a CLI triggered by user keypress. No concurrency benefit.

### 2. Streaming Pattern (D-04, D-05)

User decided to buffer streamed response, parse WHY/FIX after stream ends:

```python
def call_ollama(prompt: str) -> str:
    """Stream from Ollama, buffer full response."""
    response_text = ""
    for chunk in client.chat(
        model='gemma3:4b',
        messages=[
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': prompt}
        ],
        stream=True
    ):
        response_text += chunk['message']['content']
    return response_text
```

**Alternative (rejected by user):** Print during stream — would require real-time parsing of WHY/FIX labels which is fragile.

### 3. Error Handling (D-08, D-09, D-10)

```python
import httpx
import ollama

try:
    response = call_ollama(prompt)
except httpx.TimeoutException:
    print("[explainer offline]")
    sys.exit(0)  # Graceful exit per D-08
except ollama.ResponseError:
    print("[explainer offline]")
    sys.exit(0)
except Exception:
    print("[explainer offline]")
    sys.exit(0)
```

**Key insight:** Never exit non-zero — failures should be invisible, not disruptive.

### 4. Rich Formatting (D-06, D-07)

User decided: dim gray WHY, bold green FIX, two lines max:

```python
from rich.console import Console
from rich.style import Style

console = Console()

# Parse WHY/FIX from response
why_text = extract_why(response)
fix_text = extract_fix(response)

# Print with Rich styling
console.print(f"WHY: {why_text}", style="dim")        # Dim gray
console.print(f"FIX: {fix_text}", style="bold green") # Bold green
```

---

## Prompt Engineering

### System Prompt (D-01, D-02, D-03)

User decisions:
- D-01: Use system + user message format
- D-02: Ask for `WHY: <sentence>\nFIX: <command>` format
- D-03: Shell-aware (mention zsh, common patterns)

**Recommended system prompt:**
```python
SYSTEM_PROMPT = """You are a shell error explainer for zsh. 
Given a failed command, stderr, and exit code, explain briefly.

Output format (REQUIRED):
WHY: <one sentence explanation of what went wrong>
FIX: <the command to fix it>

Keep WHY to one sentence. FIX should be a valid shell command.
Do not include any other text or explanation."""
```

### User Prompt Construction

```python
def build_user_prompt(cmd: str, stderr: str, exit_code: int) -> str:
    return f"""Command: {cmd}
Exit code: {exit_code}
Stderr: {stderr}

Explain this error."""
```

---

## Response Parsing

### WHY/FIX Extraction (D-02, D-10)

Per D-10, unparseable response should print raw output.

```python
import re

def parse_response(response: str) -> tuple[str, str]:
    """Parse WHY and FIX from LLM response.
    
    Returns:
        (why, fix) tuple
        
    Raises:
        ValueError: If parsing fails
    """
    # Try standard format first
    why_match = re.search(r'WHY:\s*(.+?)(?=\nFIX:|$)', response, re.DOTALL)
    fix_match = re.search(r'FIX:\s*(.+?)$', response, re.DOTALL)
    
    if why_match and fix_match:
        why = why_match.group(1).strip()
        fix = fix_match.group(1).strip()
        return why, fix
    
    raise ValueError("Could not parse WHY/FIX from response")
```

### Fallback Behavior (D-10)

```python
try:
    why, fix = parse_response(response)
    console.print(f"WHY: {why}", style="dim")
    console.print(f"FIX: {fix}", style="bold green")
except ValueError:
    # Print raw output — user still gets value
    console.print(response)
```

---

## Integration Points

### Reading Temp Files (CLI-01)

Files to read:
- `/tmp/shell-explainer-last-cmd` — command text (no trailing newline)
- `/tmp/shell-explainer-last-stderr` — stderr output
- `/tmp/shell-explainer-last-exit` — exit code (integer as string)

```python
from pathlib import Path

TEMP_CMD = Path("/tmp/shell-explainer-last-cmd")
TEMP_STDERR = Path("/tmp/shell-explainer-last-stderr")
TEMP_EXIT = Path("/tmp/shell-explainer-last-exit")

def read_context() -> tuple[str, str, int]:
    """Read captured command context from temp files."""
    cmd = TEMP_CMD.read_text().strip()
    stderr = TEMP_STDERR.read_text().strip()
    exit_code = int(TEMP_EXIT.read_text().strip())
    return cmd, stderr, exit_code
```

**Note:** Files written by Phase 1's precmd hook, no trailing newline issues.

### CLI Entry Point

Existing stub in `src/errormux/cli.py`:

```python
@app.command()
def explain() -> None:
    """Explain the last failed command."""
    # Phase 2: Replace stub with real implementation
    ...
```

---

## Validation Architecture

### Testable Behaviors

| Behavior | How to Test |
|----------|-------------|
| Reads temp files correctly | Mock files, verify parsing |
| Calls Ollama with correct prompt | Mock client, check messages |
| Streams and buffers response | Mock streaming generator |
| Parses WHY/FIX format | Unit test regex |
| Handles timeout gracefully | Mock TimeoutException |
| Handles service down gracefully | Mock ResponseError |
| Prints dim WHY, bold green FIX | Capture Console output |
| Exits 0 on all failures | Check sys.exit(0) called |

### Mocking Strategy

```python
# tests/test_cli.py
import pytest
from unittest.mock import patch, MagicMock
import httpx
import ollama

def test_timeout_prints_offline():
    """D-08: Timeout should print '[explainer offline]' and exit 0."""
    with patch('ollama.Client.chat', side_effect=httpx.TimeoutException):
        with patch('sys.exit') as mock_exit:
            # Call CLI
            # Verify: prints "[explainer offline]", exits 0
            ...

def test_why_fix_parsing():
    """D-02: Parse WHY: and FIX: labels correctly."""
    response = "WHY: File not found.\nFIX: touch myfile.txt"
    why, fix = parse_response(response)
    assert why == "File not found."
    assert fix == "touch myfile.txt"
```

---

## Common Pitfalls

### 1. httpx Timeout Exception Location

**Wrong:**
```python
import httpx
# httpx.TimeoutException doesn't exist at top level
```

**Correct:**
```python
from httpx import TimeoutException
# OR handle via ollama.ResponseError which wraps it
```

### 2. Streaming vs Non-Streaming Response Shape

Streaming returns generator of chunks, non-streaming returns `ChatResponse` object directly.

**Streaming:**
```python
for chunk in client.chat(..., stream=True):
    # chunk['message']['content'] is a string
```

**Non-streaming:**
```python
response = client.chat(..., stream=False)
# response.message.content
```

### 3. Temp Files May Not Exist

Handle missing files gracefully:
```python
try:
    cmd = TEMP_CMD.read_text()
except FileNotFoundError:
    print("[errormux] No command captured")
    sys.exit(0)
```

---

## Security Considerations

### Trust Boundaries

| Boundary | Risk | Mitigation |
|----------|------|------------|
| Temp files → CLI | User-controlled content | No execution, just display |
| CLI → Ollama | Local trusted service | No auth needed, localhost only |
| Ollama → CLI | LLM output | Parse safely, no shell eval |

### Threat Model

**T-02-01: Command Injection in Output**
- Risk: FIX command printed to terminal could be accidentally executed
- Mitigation: Print as text only, no clipboard or auto-execution
- Accept: User must manually run the fix

**T-02-02: Path Traversal in Temp Files**
- Risk: Symlink attack on temp files
- Accept: Single-user local machine, /tmp is world-writable by design

---

## File Modifications

### Files to Modify

| File | Changes |
|------|---------|
| `src/errormux/cli.py` | Replace stub with real implementation |
| `pyproject.toml` | Add `ollama` dependency |

### Files to Create

None — extend existing CLI module.

---

## Recommended Implementation Order

1. Add `ollama` dependency to pyproject.toml
2. Create prompt construction module (system prompt, user prompt)
3. Create response parsing module (WHY/FIX extraction)
4. Create Ollama client wrapper with timeout and error handling
5. Update CLI explain() command to orchestrate the flow
6. Test each component independently

---

## Validation Requirements

### Dimension 1: Must-Have Truths
- User runs `??` after failed command, sees WHY and FIX output
- Output is two lines: dim WHY, bold green FIX
- Timeout prints "[explainer offline]" and exits 0

### Dimension 2: Artifacts
- `src/errormux/cli.py` contains real implementation
- `pyproject.toml` has ollama dependency

### Dimension 3: Key Links
- cli.py imports ollama.Client
- cli.py reads from temp files
- cli.py prints via Rich Console

### Dimension 4: Error Handling
- Timeout → "[explainer offline]", exit 0
- Service down → "[explainer offline]", exit 0
- Parse failure → raw output printed

### Dimension 5: Security
- No shell execution of FIX command
- Temp files read-only (no modification)

### Dimension 6: Performance
- Response within 10s (hard timeout)
- Streaming for perceived speed

### Dimension 7: Edge Cases
- Empty temp files → graceful message
- Malformed LLM response → raw output
- Binary in stderr → decode safely

### Dimension 8: Validation Strategy
- Mock Ollama client for unit tests
- Mock temp files for integration tests
- Manual testing with real Ollama for E2E

---

## References

- [ollama-python GitHub](https://github.com/ollama/ollama-python) — Official SDK docs
- [ollama PyPI](https://pypi.org/project/ollama/) — Version 0.6.1
- [Rich Console docs](https://rich.readthedocs.io/en/stable/reference/console.html) — Styling API
- [httpx docs](https://www.python-httpx.org/) — Timeout handling

---

*Research completed: 2026-04-15*
