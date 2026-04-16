"""SQLite cache for LLM explanations."""

import hashlib
import sqlite3
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".shell-explainer"
CACHE_DB = CACHE_DIR / "cache.db"
TTL_SECONDS = 7 * 24 * 60 * 60


def make_cache_key(model: str, cmd: str, stderr: str) -> str:
    """Generate SHA256 cache key from model, command, and stderr."""
    return hashlib.sha256(f"{model}|{cmd}|{stderr}".encode()).hexdigest()


def _ensure_db() -> None:
    """Create cache directory and table if not exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(CACHE_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            response TEXT NOT NULL,
            created_at REAL NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON cache(created_at)")
    conn.commit()
    conn.close()


def cache_get(key: str) -> str | None:
    """Get cached response if exists and not expired."""
    _ensure_db()
    conn = sqlite3.connect(CACHE_DB)
    cursor = conn.execute(
        "SELECT response, created_at FROM cache WHERE key = ?", (key,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    response, created_at = row
    if time.time() - created_at > TTL_SECONDS:
        cache_delete(key)
        return None

    return response


def cache_set(key: str, response: str) -> None:
    """Store response in cache with current timestamp."""
    _ensure_db()
    conn = sqlite3.connect(CACHE_DB)
    conn.execute(
        "INSERT OR REPLACE INTO cache (key, response, created_at) VALUES (?, ?, ?)",
        (key, response, time.time()),
    )
    conn.commit()
    conn.close()


def cache_delete(key: str) -> None:
    """Delete cached response."""
    conn = sqlite3.connect(CACHE_DB)
    conn.execute("DELETE FROM cache WHERE key = ?", (key,))
    conn.commit()
    conn.close()


def cache_clear() -> None:
    """Clear all cached responses."""
    conn = sqlite3.connect(CACHE_DB)
    conn.execute("DELETE FROM cache")
    conn.commit()
    conn.close()
