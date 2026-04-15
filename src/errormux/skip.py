"""Skip-list filtering: suppress LLM explanations for semantically-expected non-zero exits.

Built-in defaults cover grep/test/[[/[/diff at exit 1. Users can extend or disable
entries via ~/.shell-explainer/config.toml. Missing or malformed config degrades
silently to built-ins (per CONTEXT D-09).
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

# Built-in skip rules: (command_name -> set of exit codes to skip).
# Per CONTEXT D-02.
BUILTIN_SKIP_RULES: dict[str, set[int]] = {
    "grep": {1},
    "test": {1},
    "[[": {1},
    "[": {1},
    "diff": {1},
}

_DEFAULT_CONFIG_PATH = Path.home() / ".shell-explainer" / "config.toml"

# Matches a leading env assignment token like FOO=bar or _FOO1=.
_ENV_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def extract_command_name(command_line: str) -> str:
    """Return the first non-env-assignment token from a command line.

    'FOO=bar grep x' -> 'grep'
    'grep foo'       -> 'grep'
    ''               -> ''
    """
    if not command_line:
        return ""
    for token in command_line.split():
        if _ENV_ASSIGN_RE.match(token):
            continue
        return token
    return ""


def _builtins_copy() -> dict[str, set[int]]:
    return {k: set(v) for k, v in BUILTIN_SKIP_RULES.items()}


def load_skip_rules(config_path: Path | None = None) -> dict[str, set[int]]:
    """Load skip rules, merging built-ins with user TOML config.

    Expected config shape:

        [skip]
        disable = ["grep"]          # drop these built-ins

        [[skip.rules]]              # additive entries
        command = "make"
        exit_code = 2

    Missing file or parse errors degrade silently to built-ins (D-09).
    """
    rules = _builtins_copy()
    path = config_path if config_path is not None else _DEFAULT_CONFIG_PATH

    try:
        if not path.exists():
            return rules
    except OSError:
        return rules

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError, ValueError):
        return rules

    skip_section = data.get("skip") if isinstance(data, dict) else None
    if not isinstance(skip_section, dict):
        return rules

    # Apply disable list.
    try:
        disable = skip_section.get("disable", [])
        if isinstance(disable, list):
            for name in disable:
                if isinstance(name, str):
                    rules.pop(name, None)
    except Exception:
        pass

    # Apply additive rules.
    try:
        rules_list = skip_section.get("rules", [])
        if isinstance(rules_list, list):
            for entry in rules_list:
                try:
                    if not isinstance(entry, dict):
                        continue
                    cmd = entry.get("command")
                    code = entry.get("exit_code")
                    if not isinstance(cmd, str) or not cmd:
                        continue
                    rules.setdefault(cmd, set()).add(int(code))
                except (TypeError, ValueError):
                    continue
    except Exception:
        pass

    return rules


def should_skip(
    command_name: str,
    exit_code: int,
    rules: dict[str, set[int]] | None = None,
) -> bool:
    """Return True if (command_name, exit_code) matches a skip rule.

    Lazy-loads rules from default config when `rules` is None.
    """
    if rules is None:
        rules = load_skip_rules()
    return exit_code in rules.get(command_name, set())
