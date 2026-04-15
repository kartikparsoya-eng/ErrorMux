"""Tests for skip-list module."""

import pytest

from errormux.skip import (
    BUILTIN_SKIP_RULES,
    extract_command_name,
    load_skip_rules,
    should_skip,
)


# --- Built-in skip rules ---

def test_builtin_grep_exit_1_skipped():
    assert should_skip("grep", 1) is True


def test_builtin_grep_exit_2_not_skipped():
    """Real grep errors (exit 2) should pass through."""
    assert should_skip("grep", 2) is False


def test_builtin_test_and_bracket_skipped():
    assert should_skip("test", 1) is True
    assert should_skip("[[", 1) is True
    assert should_skip("[", 1) is True


def test_builtin_diff_exit_1_skipped():
    assert should_skip("diff", 1) is True


def test_unknown_command_not_skipped():
    assert should_skip("ls", 1) is False


# --- extract_command_name ---

def test_extract_command_name_simple():
    assert extract_command_name("grep foo bar") == "grep"


def test_extract_command_name_env_prefix():
    assert extract_command_name("FOO=bar BAZ=1 grep x") == "grep"


def test_extract_command_name_empty():
    assert extract_command_name("") == ""


def test_extract_command_name_only_env():
    """All-env-assignment line returns empty string."""
    assert extract_command_name("FOO=bar BAZ=1") == ""


# --- User config loading ---

def test_user_config_add_rule(tmp_path):
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        '[[skip.rules]]\ncommand = "make"\nexit_code = 2\n'
    )
    rules = load_skip_rules(cfg)
    assert should_skip("make", 2, rules) is True
    # Built-ins still present
    assert should_skip("grep", 1, rules) is True


def test_user_config_disable_builtin(tmp_path):
    cfg = tmp_path / "config.toml"
    cfg.write_text('[skip]\ndisable = ["grep"]\n')
    rules = load_skip_rules(cfg)
    assert should_skip("grep", 1, rules) is False
    # Other built-ins unaffected
    assert should_skip("diff", 1, rules) is True


def test_missing_config_falls_back(tmp_path):
    nonexistent = tmp_path / "does_not_exist.toml"
    rules = load_skip_rules(nonexistent)
    # Should equal built-ins
    assert rules == {k: set(v) for k, v in BUILTIN_SKIP_RULES.items()}


def test_malformed_config_falls_back(tmp_path):
    cfg = tmp_path / "config.toml"
    cfg.write_text("this is not { valid toml ===\n[[[")
    rules = load_skip_rules(cfg)
    assert rules == {k: set(v) for k, v in BUILTIN_SKIP_RULES.items()}
