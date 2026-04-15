"""Response parser for WHY/FIX extraction."""

import re


class ParseError(Exception):
    """Raised when LLM response cannot be parsed."""

    pass


def parse_response(response: str) -> tuple[str, str]:
    """Parse WHY and FIX from LLM response.

    Args:
        response: Raw LLM response text

    Returns:
        Tuple of (why, fix) strings

    Raises:
        ParseError: If WHY or FIX sections cannot be found
    """
    # Case-insensitive matching for labels
    why_match = re.search(r"(?i)why:\s*(.+?)(?=\nfix:|$)", response, re.DOTALL)
    fix_match = re.search(r"(?i)fix:\s*(.+?)$", response, re.DOTALL)

    if why_match and fix_match:
        why = why_match.group(1).strip()
        fix = fix_match.group(1).strip()
        return why, fix

    raise ParseError("Could not parse WHY/FIX from response")


def format_output(why: str, fix: str) -> str:
    """Format WHY and FIX for display.

    Args:
        why: WHY explanation text
        fix: FIX command text

    Returns:
        Formatted string for display
    """
    return f"WHY: {why}\nFIX: {fix}"
