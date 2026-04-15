# Stack Research

**Domain:** zsh plugin with Python CLI backend + Ollama local LLM integration
**Researched:** 2026-04-15
**Confidence:** HIGH

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12+ | Runtime | Modern async support, performance improvements, standard for CLI tools. 3.12 has significant optimizations over 3.11. |
| uv | 0.5+ | Package manager | 10-100x faster than pip. Replaces pip, pip-tools, pipx, poetry, pyenv, virtualenv. Single tool for dependency management, virtual environments, and Python version management. Written in Rust, actively maintained by Astral (Ruff creators). |
| ollama | 0.6.1 | Ollama Python SDK | Official Python client for Ollama. Wraps httpx internally with proper error handling, streaming support, and typed responses. Simpler than raw httpx calls. Supports both sync and async clients. |
| typer | 0.15+ | CLI framework | "FastAPI of CLIs" - built on Click with type hints for automatic help generation, shell completion, and Rich integration. Minimal boilerplate (2 lines for simplest CLI). Excellent editor support. |
| rich | 14.0+ | Terminal output | Beautiful terminal formatting, progress bars, live displays, and syntax highlighting. Integrated with Typer for automatic error formatting. Industry standard for Python CLI output. |
| SQLite | (stdlib) | Cache storage | Zero-config, single-file database, included in Python stdlib. Fast for key-value lookups with SHA256 cache keys. 7-day TTL is trivial to implement. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| httpx | 0.28+ | HTTP client (fallback) | If you need direct HTTP control outside ollama SDK. The ollama library uses httpx internally, so it's already a dependency. |
| pytest | 8.0+ | Testing framework | For test suite covering cache, skip-list, and prompt construction. |
| pytest-asyncio | 0.24+ | Async test support | If using async client for concurrent requests. |

### Shell Integration

| Component | Purpose | Notes |
|-----------|---------|-------|
| preexec hook | Captures command before execution | Stores command text in global variable |
| precmd hook | Captures exit code and stderr after execution | Stores exit status, triggers on next prompt |
| zle widget (`??`) | User-triggered explanation | Binds to key sequence, calls Python CLI |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Dependency management | Replaces pip/poetry. Use `uv add`, `uv sync`, `uv run` |
| ruff | Linting/formatting | Fast, comprehensive. Optional but recommended |
| pytest | Test runner | `uv run pytest` |

## Installation

```bash
# Initialize project with uv
uv init errormux
cd errormux

# Add dependencies
uv add ollama typer rich

# Add dev dependencies
uv add --dev pytest pytest-asyncio

# Run the CLI
uv run errormux --help
```

### Zsh Plugin Installation

```zsh
# In ~/.zshrc
source ~/.zsh/plugins/errormux/errormux.plugin.zsh
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| ollama SDK | httpx direct | If you need fine-grained HTTP control, custom timeouts per request, or non-standard endpoints. The ollama SDK exposes httpx Client kwargs, so customization is possible. |
| ollama SDK | requests | Legacy projects only. httpx is the modern standard - requests doesn't support async or HTTP/2. |
| uv | poetry | If your team is already invested in poetry. But uv is faster and simpler. |
| typer | click directly | If you need Click's lower-level control. Typer is Click + type hints + Rich. |
| typer | argparse | Only for stdlib-only constraint. Typer is worth the dependency. |
| SQLite | Redis | Only if you need distributed caching or TTL precision < 1 second. Overkill for single-user local tool. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| requests library | Synchronous only, no HTTP/2, no streaming support, being superseded by httpx | httpx or ollama SDK |
| poetry | 10-100x slower than uv, more complex configuration | uv |
| pip + virtualenv | Manual management, slower dependency resolution | uv |
| argparse | Verbose, no automatic help generation, no shell completion | typer |
| Global Python packages | Pollutes system, version conflicts | uv project environments |
| Redis/external DB | Unnecessary complexity for single-user local cache | SQLite |
| Subprocess calls to ollama CLI | Slower, no streaming, fragile parsing | ollama Python SDK |

## Stack Patterns by Variant

**If streaming is critical:**
- Use `ollama.chat()` with `stream=True`
- Iterate over chunks, print incrementally
- Rich Live for animated output

**If timeout is strict (10s):**
- ollama SDK supports timeout via httpx kwargs: `Client(timeout=10.0)`
- Handle `httpx.TimeoutException` gracefully

**If offline-first is required:**
- Check ollama service availability before requests
- Cache should handle fallback gracefully
- ollama SDK raises `ResponseError` on connection failure

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| ollama 0.6.1 | httpx 0.27+ | ollama depends on httpx internally |
| typer 0.15+ | rich 13+ | typer bundles rich for error formatting |
| Python 3.12+ | uv 0.5+ | uv manages Python versions too |
| uv 0.5+ | all above | uv handles dependency resolution |

## Key Architecture Decisions

### Ollama SDK vs Raw httpx

**Recommendation: Use ollama SDK**

```python
# Recommended (cleaner)
from ollama import Client
client = Client(host='http://localhost:11434', timeout=10.0)
response = client.chat(model='gemma3:4b', messages=[...])

# Alternative (direct httpx - more control but more code)
import httpx
client = httpx.Client(base_url='http://localhost:11434', timeout=10.0)
response = client.post('/api/chat', json={...})
```

The ollama SDK provides:
- Typed responses (ChatResponse with `.message.content`)
- Built-in error handling (`ResponseError` with status codes)
- Streaming support via generator
- Async client option
- Passes extra kwargs to httpx for customization

### Zsh Hook Pattern

```zsh
# Capture pattern (standard approach)
_ERRORMUX_CMD=""
_ERRORMUX_STDERR=""

_errormux_preexec() {
    _ERRORMUX_CMD="$1"
}

_errormux_precmd() {
    local exit_code=$?
    # Store exit code, stderr captured separately
}

preexec_functions+=(_errormux_preexec)
precmd_functions+=(_errormux_precmd)
```

### Cache Key Strategy

```python
import hashlib

def cache_key(command: str, exit_code: int, stderr: str) -> str:
    """SHA256 hash for deterministic cache keys"""
    data = f"{command}|{exit_code}|{stderr}"
    return hashlib.sha256(data.encode()).hexdigest()
```

## Sources

- [uv docs](https://docs.astral.sh/uv/) — Package manager, verified Apr 2026 (HIGH confidence)
- [ollama-python GitHub](https://github.com/ollama/ollama-python) — Official SDK, verified Apr 2026 (HIGH confidence)
- [ollama PyPI](https://pypi.org/project/ollama/) — Version 0.6.1, Nov 2025 (HIGH confidence)
- [httpx docs](https://www.python-httpx.org/) — HTTP client, verified Apr 2026 (HIGH confidence)
- [httpx PyPI](https://pypi.org/project/httpx/) — Version 0.28.1, Dec 2024 (HIGH confidence)
- [typer docs](https://typer.tiangolo.com/) — CLI framework, verified Apr 2026 (HIGH confidence)
- [rich docs](https://rich.readthedocs.io/) — Terminal output, verified Apr 2026 (HIGH confidence)
- [Ollama API docs](https://github.com/ollama/ollama/blob/main/docs/api.md) — REST API reference (HIGH confidence)

---
*Stack research for: ErrorMux zsh plugin + Python CLI + Ollama*
*Researched: 2026-04-15*
