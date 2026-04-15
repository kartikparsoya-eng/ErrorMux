"""Tests for prompt construction."""

from errormux.prompts import SYSTEM_PROMPT, build_user_prompt


class TestSystemPrompt:
    """Tests for SYSTEM_PROMPT constant."""

    def test_contains_zsh_reference(self):
        """SYSTEM_PROMPT mentions zsh (per D-03)."""
        assert "zsh" in SYSTEM_PROMPT.lower()

    def test_contains_why_label(self):
        """SYSTEM_PROMPT contains WHY: label (per D-02)."""
        assert "WHY:" in SYSTEM_PROMPT

    def test_contains_fix_label(self):
        """SYSTEM_PROMPT contains FIX: label (per D-02)."""
        assert "FIX:" in SYSTEM_PROMPT

    def test_requests_one_sentence_why(self):
        """SYSTEM_PROMPT requests one sentence WHY."""
        assert "one sentence" in SYSTEM_PROMPT.lower()

    def test_requests_shell_command_fix(self):
        """SYSTEM_PROMPT requests FIX as valid shell command."""
        assert (
            "shell command" in SYSTEM_PROMPT.lower()
            or "command" in SYSTEM_PROMPT.lower()
        )


class TestBuildUserPrompt:
    """Tests for build_user_prompt function."""

    def test_formats_all_inputs_correctly(self):
        """build_user_prompt formats command, stderr, exit code."""
        result = build_user_prompt(
            cmd="cat myfile.txt",
            stderr="cat: myfile.txt: No such file or directory",
            exit_code=1,
        )
        assert "Command: cat myfile.txt" in result
        assert "Exit code: 1" in result
        assert "Stderr: cat: myfile.txt: No such file or directory" in result
        assert "Explain this error" in result

    def test_handles_empty_stderr(self):
        """build_user_prompt handles empty stderr."""
        result = build_user_prompt(
            cmd="ls",
            stderr="",
            exit_code=2,
        )
        assert "Command: ls" in result
        assert "Exit code: 2" in result
        assert "Stderr:" in result

    def test_handles_multiline_stderr(self):
        """build_user_prompt handles multi-line stderr."""
        result = build_user_prompt(
            cmd="make",
            stderr="error: file not found\nerror: compilation failed",
            exit_code=2,
        )
        assert "error: file not found" in result
        assert "error: compilation failed" in result

    def test_returns_string(self):
        """build_user_prompt returns a string."""
        result = build_user_prompt(cmd="ls", stderr="", exit_code=0)
        assert isinstance(result, str)
