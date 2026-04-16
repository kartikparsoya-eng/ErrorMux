"""Tests for cache module."""

import time

import pytest

from errormux.cache import (
    CACHE_DB,
    TTL_SECONDS,
    cache_get,
    cache_set,
    cache_delete,
    make_cache_key,
)


@pytest.fixture
def temp_cache_db(monkeypatch, tmp_path):
    """Create temp cache DB for isolated testing."""
    cache_dir = tmp_path / "cache"
    cache_db = cache_dir / "cache.db"

    monkeypatch.setattr("errormux.cache.CACHE_DIR", cache_dir)
    monkeypatch.setattr("errormux.cache.CACHE_DB", cache_db)

    yield cache_db


def test_cache_key_deterministic():
    """Same input produces same key."""
    key1 = make_cache_key("gemma4:e2b", "ls foo", "error")
    key2 = make_cache_key("gemma4:e2b", "ls foo", "error")
    assert key1 == key2


def test_cache_key_different_stderr():
    """Different stderr produces different key."""
    key1 = make_cache_key("gemma4:e2b", "ls foo", "error1")
    key2 = make_cache_key("gemma4:e2b", "ls foo", "error2")
    assert key1 != key2


def test_cache_key_different_cmd():
    """Different command produces different key."""
    key1 = make_cache_key("gemma4:e2b", "ls foo", "error")
    key2 = make_cache_key("gemma4:e2b", "ls bar", "error")
    assert key1 != key2


def test_cache_key_different_model():
    """Different model produces different key."""
    key1 = make_cache_key("gemma3:4b", "ls foo", "error")
    key2 = make_cache_key("gemma4:e2b", "ls foo", "error")
    assert key1 != key2


def test_cache_set_get(temp_cache_db):
    """Set and get returns stored value."""
    cache_set("testkey", "test response")
    result = cache_get("testkey")
    assert result == "test response"


def test_cache_get_missing(temp_cache_db):
    """Get missing key returns None."""
    result = cache_get("nonexistent")
    assert result is None


def test_cache_overwrite(temp_cache_db):
    """Set overwrites existing key."""
    cache_set("testkey", "first")
    cache_set("testkey", "second")
    result = cache_get("testkey")
    assert result == "second"


def test_cache_delete(temp_cache_db):
    """Delete removes cached value."""
    cache_set("testkey", "test response")
    cache_delete("testkey")
    result = cache_get("testkey")
    assert result is None


def test_cache_ttl_expiration(temp_cache_db, monkeypatch):
    """Expired entries return None."""
    import sqlite3

    cache_set("testkey", "test response")

    expired_time = time.time() + TTL_SECONDS + 1
    monkeypatch.setattr("errormux.cache.time.time", lambda: expired_time)

    result = cache_get("testkey")
    assert result is None


def test_cli_cache_hit(monkeypatch, tmp_path, capsys):
    """Cache hit returns cached response without calling Ollama."""
    from errormux import cli
    from errormux.cache import cache_set, make_cache_key

    cache_dir = tmp_path / "cache"
    cache_db = cache_dir / "cache.db"
    monkeypatch.setattr("errormux.cache.CACHE_DIR", cache_dir)
    monkeypatch.setattr("errormux.cache.CACHE_DB", cache_db)

    cmd_file = tmp_path / "cmd"
    stderr_file = tmp_path / "stderr"
    exit_file = tmp_path / "exit"
    cmd_file.write_text("ls nonexistent")
    stderr_file.write_text("No such file or directory")
    exit_file.write_text("2")

    monkeypatch.setattr(cli, "TEMP_CMD", cmd_file)
    monkeypatch.setattr(cli, "TEMP_STDERR", stderr_file)
    monkeypatch.setattr(cli, "TEMP_EXIT", exit_file)

    cache_key = make_cache_key(
        "gemma4:e2b", "ls nonexistent", "No such file or directory"
    )
    cache_set(cache_key, "WHY: Directory does not exist\nFIX: mkdir nonexistent")

    cli.explain()

    captured = capsys.readouterr()
    assert "WHY: Directory does not exist" in captured.out
    assert "FIX: mkdir nonexistent" in captured.out


def test_cli_cache_miss_then_hit(monkeypatch, tmp_path):
    """Cache miss calls Ollama, then cache hit returns cached response."""
    from errormux import cli
    from errormux.cache import cache_get, cache_set, make_cache_key

    cache_dir = tmp_path / "cache"
    cache_db = cache_dir / "cache.db"
    monkeypatch.setattr("errormux.cache.CACHE_DIR", cache_dir)
    monkeypatch.setattr("errormux.cache.CACHE_DB", cache_db)

    cmd_file = tmp_path / "cmd"
    stderr_file = tmp_path / "stderr"
    exit_file = tmp_path / "exit"
    cmd_file.write_text("ls missing")
    stderr_file.write_text("error")
    exit_file.write_text("1")

    monkeypatch.setattr(cli, "TEMP_CMD", cmd_file)
    monkeypatch.setattr(cli, "TEMP_STDERR", stderr_file)
    monkeypatch.setattr(cli, "TEMP_EXIT", exit_file)

    cache_key = make_cache_key("gemma4:e2b", "ls missing", "error")
    assert cache_get(cache_key) is None

    cache_set(cache_key, "WHY: test\nFIX: test fix")

    result = cache_get(cache_key)
    assert result == "WHY: test\nFIX: test fix"
