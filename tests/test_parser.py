"""Tests for response parser."""

import pytest

from errormux.parser import ParseError, parse_response, format_output


class TestParseResponse:
    """Tests for parse_response function."""

    def test_extracts_why_and_fix_correctly(self):
        """parse_response extracts 'WHY: foo\\nFIX: bar' correctly."""
        response = "WHY: File not found.\nFIX: touch myfile.txt"
        why, fix = parse_response(response)
        assert why == "File not found."
        assert fix == "touch myfile.txt"

    def test_handles_multi_line_why_text(self):
        """parse_response handles multi-line WHY text."""
        response = (
            "WHY: The file doesn't\nexist in the current directory.\nFIX: touch file"
        )
        why, fix = parse_response(response)
        assert why == "The file doesn't\nexist in the current directory."
        assert fix == "touch file"

    def test_raises_parse_error_for_malformed_response(self):
        """parse_response raises ParseError for malformed response."""
        response = "Some random text without labels"
        with pytest.raises(ParseError):
            parse_response(response)

    def test_handles_extra_whitespace(self):
        """parse_response handles extra whitespace around labels."""
        response = "WHY:   File not found.  \nFIX:   touch myfile.txt  "
        why, fix = parse_response(response)
        assert why == "File not found."
        assert fix == "touch myfile.txt"

    def test_handles_missing_why(self):
        """parse_response raises ParseError when WHY is missing."""
        response = "FIX: touch myfile.txt"
        with pytest.raises(ParseError):
            parse_response(response)

    def test_handles_missing_fix(self):
        """parse_response raises ParseError when FIX is missing."""
        response = "WHY: File not found."
        with pytest.raises(ParseError):
            parse_response(response)

    def test_handles_lowercase_labels(self):
        """parse_response handles lowercase why: and fix: labels."""
        response = "why: File not found.\nfix: touch myfile.txt"
        why, fix = parse_response(response)
        assert why == "File not found."
        assert fix == "touch myfile.txt"

    def test_handles_mixed_case_labels(self):
        """parse_response handles mixed case labels."""
        response = "Why: File not found.\nFix: touch myfile.txt"
        why, fix = parse_response(response)
        assert why == "File not found."
        assert fix == "touch myfile.txt"


class TestFormatOutput:
    """Tests for format_output function."""

    def test_returns_formatted_string(self):
        """format_output returns formatted string for display."""
        result = format_output("File not found.", "touch myfile.txt")
        assert result == "WHY: File not found.\nFIX: touch myfile.txt"

    def test_handles_multiline_why(self):
        """format_output handles multi-line WHY text."""
        result = format_output("The file\ndoes not exist.", "touch file")
        assert "WHY: The file" in result
        assert "does not exist." in result
        assert "FIX: touch file" in result
