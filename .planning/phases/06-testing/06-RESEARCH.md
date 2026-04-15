# Phase 6: Testing - Research

**Gathered:** 2026-04-15
**Phase:** 06-testing
**Goal:** All components verified with automated tests (80% coverage, httpx MockTransport)

---

## Research Questions

1. **pytest-cov Setup** — How to configure pytest-cov in pyproject.toml for Python 3.12+ with uv?
2. **httpx MockTransport** — How to mock httpx requests for Ollama API calls (replacing unittest.mock)?
3. **Coverage Best Practices** — How to enforce 80% threshold, exclude untestable code, and generate reports?

---

## Findings

### 1. pytest-cov Setup

**Installation:**
```bash
uv add --dev pytest-cov
```

**pyproject.toml configuration:**
```toml
[tool.pytest.ini_options]
addopts = "--cov=errormux --cov-fail-under=80 --cov-report=term-missing"
testpaths = ["tests"]

[tool.coverage.run]
source = ["src/errormux"]
omit = ["*/__main__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

**Manual run:**
```bash
uv run pytest --cov=errormux --cov-fail-under=80 --cov-report=term-missing
```

**Key features:**
- `--cov-fail-under=N` exits with error code if coverage below threshold
- `--cov-report=term-missing` shows uncovered lines
- `--cov-report=html` generates browsable HTML report in `htmlcov/`
- Coverage measured by line execution, not branch coverage (branch coverage requires `--cov-branch`)

### 2. httpx MockTransport for Ollama Mocking

**Current approach (unittest.mock):**
```python
with patch("ollama.Client") as MockClient:
    mock_instance = MagicMock()
    MockClient.return_value = mock_instance
    mock_instance.chat.return_value = iter([{"message": {"content": "response"}}])
```

**httpx MockTransport approach:**
The ollama Python SDK uses httpx internally. To mock at the httpx level:

```python
import httpx
from errormux.client import chat_with_ollama

def test_chat_with_ollama_mocked():
    def handler(request):
        # Return mock Ollama chat response
        return httpx.Response(
            200,
            json={
                "model": "gemma3:4b",
                "created_at": "2024-01-01T00:00:00Z",
                "message": {"role": "assistant", "content": "WHY: test\nFIX: test"},
                "done": True,
            }
        )
    
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, base_url="http://localhost:11434")
    
    # Patch the httpx.Client creation inside ollama.Client
    with patch("httpx.Client", return_value=client):
        result = chat_with_ollama("system", "user")
        assert "WHY:" in result
```

**Alternative: respx library (httpx mocking):**
```python
import respx
import httpx

@respx.mock
def test_chat_with_ollama():
    respx.post("http://localhost:11434/api/chat").mock(
        return_value=httpx.Response(200, json={"message": {"content": "WHY: x\nFIX: y"}})
    )
    # ... test code
```

**Note:** respx requires additional dependency. For minimal deps, use httpx.MockTransport directly.

**Streaming response mock:**
The ollama SDK uses streaming. MockTransport can handle this:
```python
def handler(request):
    # Simulate streaming response
    def iter_bytes():
        yield b'{"message":{"content":"WHY: "}}'
        yield b'{"message":{"content":"test"}}'
    return httpx.Response(200, iter_bytes=iter_bytes())
```

**Key insight:** The ollama SDK's `chat()` method with `stream=True` returns an iterator of chunks. MockTransport must provide this structure.

### 3. Coverage Best Practices

**Excluding untestable code:**
- Use `# pragma: no cover` comment on specific lines
- Use `if TYPE_CHECKING:` blocks for type-only imports
- Use coverage configuration to exclude entire files/patterns

**Common exclusions for CLI tools:**
- Entry point `__main__.py` (typically just `app()`)
- Error handlers that require external service failure
- Debug/logging code paths

**Threshold enforcement strategies:**
1. **CI gate:** Add pytest with `--cov-fail-under=80` to CI pipeline
2. **Pre-commit hook:** Run coverage check before commits
3. **PR check:** Block merge if coverage drops

**Coverage report formats:**
- `term-missing` — Terminal output with uncovered line numbers (default for CI)
- `html` — Browsable HTML report (useful for local dev)
- `xml` — Machine-readable for CI integrations (Codecov, etc.)
- `json` — For custom tooling

**Branch vs line coverage:**
- Line coverage: simpler, measures if line executed
- Branch coverage: stricter, measures if all branches taken
- For 80% threshold, line coverage is standard (add `--cov-branch` for stricter)

---

## Technical Recommendations

### D-01 Implementation (80% coverage)
```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-v --cov=errormux --cov-fail-under=80 --cov-report=term-missing"

[tool.coverage.run]
source = ["src/errormux"]
branch = false  # Line coverage only for 80% threshold

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "def __repr__",
]
```

### D-02 Implementation (httpx MockTransport)

**Option A: Direct httpx.MockTransport (no new deps)**
```python
# tests/conftest.py
import httpx
from contextlib import contextmanager

@contextmanager
def mock_ollama_response(content="WHY: test\nFIX: test"):
    def handler(request):
        # Simulate ollama chat streaming response
        chunks = [
            {"message": {"content": content}},
            {"done": True},
        ]
        import json
        def iter_lines():
            for chunk in chunks:
                yield json.dumps(chunk).encode() + b"\n"
        return httpx.Response(200, iter_bytes=iter_lines())
    
    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, base_url="http://localhost:11434")
    with patch("httpx.Client", return_value=client):
        yield
```

**Option B: Use respx library (cleaner API, adds dep)**
```python
# tests/conftest.py
import respx
import httpx

@respx.mock
def mock_ollama_chat(content="WHY: test\nFIX: test"):
    respx.post("http://localhost:11434/api/chat").mock(
        return_value=httpx.Response(200, json={"message": {"content": content}})
    )
```

**Recommendation:** Use **Option A** (direct httpx.MockTransport) to maintain minimal dependencies per PROJECT.md constraints.

### D-03 Implementation (pytest-cov)

**Add to pyproject.toml:**
```toml
[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]
```

**Run command:**
```bash
uv run pytest --cov=errormux --cov-fail-under=80
```

---

## Existing Test Analysis

**Current test coverage (estimated):**
- `tests/test_cache.py` — 10 tests, covers cache.py fully
- `tests/test_skip.py` — 11 tests, covers skip.py fully
- `tests/test_prompts.py` — 10 tests, covers prompts.py fully
- `tests/test_cli.py` — 18 tests, covers cli.py (skip integration, error handling)
- `tests/test_parser.py` — 10 tests, covers parser.py fully
- `tests/test_client.py` — 6 tests, covers client.py (uses unittest.mock — needs conversion)

**Total: 63 tests passing**

**Gaps to address:**
1. `test_client.py` uses `unittest.mock.patch` — convert to httpx MockTransport
2. No coverage measurement — add pytest-cov
3. No coverage threshold enforcement — add `--cov-fail-under=80`

---

## Validation Architecture

### Test Categories (Nyquist Dimension 8)

| Category | Tests | Validation Method |
|----------|-------|-------------------|
| Cache operations | test_cache.py | In-memory SQLite, TTL mocking |
| Skip-list logic | test_skip.py | Command extraction, config loading |
| Prompt building | test_prompts.py | String assertions |
| Response parsing | test_parser.py | WHY/FIX extraction |
| Ollama client | test_client.py | httpx MockTransport |
| CLI integration | test_cli.py | Typer CliRunner, mocked dependencies |

### Coverage Targets per Module

| Module | Target | Notes |
|--------|--------|-------|
| cache.py | 90%+ | Core logic, well-tested |
| skip.py | 90%+ | Core logic, well-tested |
| prompts.py | 100% | Simple functions |
| parser.py | 100% | Simple functions |
| client.py | 80%+ | Mock Ollama calls |
| cli.py | 75%+ | Error paths, skip integration |

---

## References

- [pytest-cov docs](https://pytest-cov.readthedocs.io/) — Coverage plugin configuration
- [httpx MockTransport](https://www.python-httpx.org/advanced/#testing) — Official mocking approach
- [httpx transports](https://www.python-httpx.org/advanced/#custom-transports) — Transport layer docs
- [Coverage.py config](https://coverage.readthedocs.io/en/latest/config.html) — Configuration reference

---

*Research completed: 2026-04-15*
