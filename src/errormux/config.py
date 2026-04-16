"""Configuration management for ErrorMux."""

from pathlib import Path

import tomli

CONFIG_DIR = Path.home() / ".shell-explainer"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG = """# ErrorMux Configuration
# Generated automatically on first run

[model]
# Required: Ollama model for explanations
# Install: ollama pull gemma4:e2b
name = "gemma4:e2b"
"""


def ensure_config() -> None:
    """Create config file if it doesn't exist, purge old cache."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    is_first_run = not CONFIG_FILE.exists()

    if is_first_run:
        CONFIG_FILE.write_text(DEFAULT_CONFIG)
        # Purge old cache entries (different model)
        from errormux.cache import cache_clear

        cache_clear()


def get_model_name() -> str:
    """Get model name from config file."""
    ensure_config()
    with open(CONFIG_FILE, "rb") as f:
        config = tomli.load(f)
    return config.get("model", {}).get("name", "gemma4:e2b")
