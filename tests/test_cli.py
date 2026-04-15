"""Tests for CLI explain command."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os

from typer.testing import CliRunner

from errormux.cli import app, explain, read_context


class TestForceFlag:
    """Tests for --force/-f flag presence."""

    def test_force_flag_in_help(self):
        """explain command advertises --force and -f in help output."""
        runner = CliRunner()
        result = runner.invoke(app, ["explain", "--help"])
        assert result.exit_code == 0
        assert "--force" in result.output
        assert "-f" in result.output


class TestReadContext:
    """Tests for read_context function."""

    def test_reads_all_temp_files(self):
        """read_context reads all three temp files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_file = Path(tmpdir) / "shell-explainer-last-cmd"
            stderr_file = Path(tmpdir) / "shell-explainer-last-stderr"
            exit_file = Path(tmpdir) / "shell-explainer-last-exit"

            cmd_file.write_text("cat myfile.txt")
            stderr_file.write_text("cat: myfile.txt: No such file or directory")
            exit_file.write_text("1")

            with patch("errormux.cli.TEMP_CMD", cmd_file):
                with patch("errormux.cli.TEMP_STDERR", stderr_file):
                    with patch("errormux.cli.TEMP_EXIT", exit_file):
                        cmd, stderr, exit_code = read_context()
                        assert cmd == "cat myfile.txt"
                        assert stderr == "cat: myfile.txt: No such file or directory"
                        assert exit_code == 1

    def test_raises_filenotfound_for_missing_files(self):
        """read_context raises FileNotFoundError for missing temp files."""
        with patch("errormux.cli.TEMP_CMD", Path("/nonexistent/cmd")):
            with pytest.raises(FileNotFoundError):
                read_context()


class TestExplain:
    """Tests for explain() command."""

    def test_prints_why_in_dim_gray(self):
        """explain() prints WHY in dim gray (D-07)."""
        mock_console = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_file = Path(tmpdir) / "shell-explainer-last-cmd"
            stderr_file = Path(tmpdir) / "shell-explainer-last-stderr"
            exit_file = Path(tmpdir) / "shell-explainer-last-exit"

            cmd_file.write_text("cat myfile.txt")
            stderr_file.write_text("cat: myfile.txt: No such file or directory")
            exit_file.write_text("1")

            with patch("errormux.cli.TEMP_CMD", cmd_file):
                with patch("errormux.cli.TEMP_STDERR", stderr_file):
                    with patch("errormux.cli.TEMP_EXIT", exit_file):
                        with patch("errormux.cli.Console") as MockConsole:
                            MockConsole.return_value = mock_console
                            with patch("errormux.cli.chat_with_ollama") as mock_chat:
                                mock_chat.return_value = (
                                    "WHY: File not found.\nFIX: touch myfile.txt"
                                )

                                explain()

                                # Check WHY was printed with dim style
                                why_calls = [
                                    c
                                    for c in mock_console.print.call_args_list
                                    if "WHY:" in str(c)
                                ]
                                assert len(why_calls) == 1
                                assert why_calls[0].kwargs.get("style") == "dim"

    def test_prints_fix_in_bold_green(self):
        """explain() prints FIX in bold green (D-07)."""
        mock_console = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_file = Path(tmpdir) / "shell-explainer-last-cmd"
            stderr_file = Path(tmpdir) / "shell-explainer-last-stderr"
            exit_file = Path(tmpdir) / "shell-explainer-last-exit"

            cmd_file.write_text("cat myfile.txt")
            stderr_file.write_text("cat: myfile.txt: No such file or directory")
            exit_file.write_text("1")

            with patch("errormux.cli.TEMP_CMD", cmd_file):
                with patch("errormux.cli.TEMP_STDERR", stderr_file):
                    with patch("errormux.cli.TEMP_EXIT", exit_file):
                        with patch("errormux.cli.Console") as MockConsole:
                            MockConsole.return_value = mock_console
                            with patch("errormux.cli.chat_with_ollama") as mock_chat:
                                mock_chat.return_value = (
                                    "WHY: File not found.\nFIX: touch myfile.txt"
                                )

                                explain()

                                # Check FIX was printed with bold green style
                                fix_calls = [
                                    c
                                    for c in mock_console.print.call_args_list
                                    if "FIX:" in str(c)
                                ]
                                assert len(fix_calls) == 1
                                assert fix_calls[0].kwargs.get("style") == "bold green"

    def test_handles_timeout_with_offline_message(self):
        """explain() handles timeout with '[explainer offline]' and exit 0 (D-08)."""
        mock_console = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_file = Path(tmpdir) / "shell-explainer-last-cmd"
            stderr_file = Path(tmpdir) / "shell-explainer-last-stderr"
            exit_file = Path(tmpdir) / "shell-explainer-last-exit"

            cmd_file.write_text("cat myfile.txt")
            stderr_file.write_text("error")
            exit_file.write_text("1")

            with patch("errormux.cli.TEMP_CMD", cmd_file):
                with patch("errormux.cli.TEMP_STDERR", stderr_file):
                    with patch("errormux.cli.TEMP_EXIT", exit_file):
                        with patch("errormux.cli.Console") as MockConsole:
                            MockConsole.return_value = mock_console
                            with patch("errormux.cli.chat_with_ollama") as mock_chat:
                                mock_chat.side_effect = TimeoutError("timed out")

                                explain()

                                # Check offline message was printed
                                mock_console.print.assert_called()
                                calls_str = str(mock_console.print.call_args_list)
                                assert "[explainer offline]" in calls_str

    def test_handles_unparseable_response(self):
        """explain() handles unparseable response by printing raw output (D-10)."""
        mock_console = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_file = Path(tmpdir) / "shell-explainer-last-cmd"
            stderr_file = Path(tmpdir) / "shell-explainer-last-stderr"
            exit_file = Path(tmpdir) / "shell-explainer-last-exit"

            cmd_file.write_text("cat myfile.txt")
            stderr_file.write_text("error")
            exit_file.write_text("1")

            with patch("errormux.cli.TEMP_CMD", cmd_file):
                with patch("errormux.cli.TEMP_STDERR", stderr_file):
                    with patch("errormux.cli.TEMP_EXIT", exit_file):
                        with patch("errormux.cli.Console") as MockConsole:
                            MockConsole.return_value = mock_console
                            with patch("errormux.cli.chat_with_ollama") as mock_chat:
                                # Response without WHY/FIX labels
                                mock_chat.return_value = (
                                    "Some random text without labels"
                                )

                                explain()

                                # Raw output should be printed
                                mock_console.print.assert_called()
                                calls_str = str(mock_console.print.call_args_list)
                                assert "Some random text without labels" in calls_str

    def test_handles_missing_temp_files_gracefully(self):
        """explain() handles missing temp files with graceful message."""
        mock_console = MagicMock()

        with patch("errormux.cli.TEMP_CMD", Path("/nonexistent/cmd")):
            with patch("errormux.cli.Console") as MockConsole:
                MockConsole.return_value = mock_console

                explain()

                # Check graceful message was printed
                mock_console.print.assert_called()
                calls_str = str(mock_console.print.call_args_list)
                assert "No command captured" in calls_str

    def test_handles_connection_error_with_offline_message(self):
        """explain() handles ConnectionError with '[explainer offline]'."""
        mock_console = MagicMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_file = Path(tmpdir) / "shell-explainer-last-cmd"
            stderr_file = Path(tmpdir) / "shell-explainer-last-stderr"
            exit_file = Path(tmpdir) / "shell-explainer-last-exit"

            cmd_file.write_text("cat myfile.txt")
            stderr_file.write_text("error")
            exit_file.write_text("1")

            with patch("errormux.cli.TEMP_CMD", cmd_file):
                with patch("errormux.cli.TEMP_STDERR", stderr_file):
                    with patch("errormux.cli.TEMP_EXIT", exit_file):
                        with patch("errormux.cli.Console") as MockConsole:
                            MockConsole.return_value = mock_console
                            with patch("errormux.cli.chat_with_ollama") as mock_chat:
                                mock_chat.side_effect = ConnectionError("service down")

                                explain()

                                # Check offline message was printed
                                mock_console.print.assert_called()
                                calls_str = str(mock_console.print.call_args_list)
                                assert "[explainer offline]" in calls_str


class TestSkipIntegration:
    """Tests for skip-list short-circuit behavior in explain() (SKIP-01..04, D-03/D-04/D-10/D-11)."""

    def _setup(self, tmpdir, cmd_text, stderr_text, exit_text):
        cmd_file = Path(tmpdir) / "shell-explainer-last-cmd"
        stderr_file = Path(tmpdir) / "shell-explainer-last-stderr"
        exit_file = Path(tmpdir) / "shell-explainer-last-exit"
        cmd_file.write_text(cmd_text)
        stderr_file.write_text(stderr_text)
        exit_file.write_text(exit_text)
        return cmd_file, stderr_file, exit_file

    def _run_explain(self, cmd_text, stderr_text, exit_text, force=False):
        """Invoke explain() with patched temp files and mocks."""
        mock_console = MagicMock()
        mock_chat = MagicMock(return_value="WHY: x\nFIX: y")
        mock_cache_set = MagicMock()
        mock_cache_get = MagicMock(return_value=None)

        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_file, stderr_file, exit_file = self._setup(
                tmpdir, cmd_text, stderr_text, exit_text
            )
            with patch("errormux.cli.TEMP_CMD", cmd_file), \
                 patch("errormux.cli.TEMP_STDERR", stderr_file), \
                 patch("errormux.cli.TEMP_EXIT", exit_file), \
                 patch("errormux.cli.Console", return_value=mock_console), \
                 patch("errormux.cli.chat_with_ollama", mock_chat), \
                 patch("errormux.cli.cache_set", mock_cache_set), \
                 patch("errormux.cli.cache_get", mock_cache_get):
                explain(force=force)
        return mock_console, mock_chat, mock_cache_set, mock_cache_get

    def test_explain_skips_grep_exit_1(self):
        """grep exit 1 short-circuits: dim notice, no LLM, no cache_set (SKIP-01)."""
        console, chat, cache_set_m, _ = self._run_explain("grep foo file", "", "1")
        chat.assert_not_called()
        cache_set_m.assert_not_called()
        calls_str = str(console.print.call_args_list)
        assert "grep" in calls_str
        assert "exit 1" in calls_str
        notice_calls = [
            c for c in console.print.call_args_list
            if "nothing to explain" in str(c)
        ]
        assert len(notice_calls) == 1
        assert notice_calls[0].kwargs.get("style") == "dim"

    def test_explain_skips_diff_exit_1(self):
        """diff exit 1 short-circuits (SKIP-03)."""
        console, chat, cache_set_m, _ = self._run_explain("diff a b", "", "1")
        chat.assert_not_called()
        cache_set_m.assert_not_called()
        assert "diff" in str(console.print.call_args_list)

    def test_explain_skips_test_exit_1(self):
        """test exit 1 short-circuits (SKIP-02)."""
        console, chat, cache_set_m, _ = self._run_explain("test -f x", "", "1")
        chat.assert_not_called()
        cache_set_m.assert_not_called()
        assert "test" in str(console.print.call_args_list)

    def test_explain_force_bypasses_skip(self):
        """--force bypasses skip list; normal flow runs (D-11)."""
        _, chat, cache_set_m, cache_get_m = self._run_explain(
            "grep foo file", "", "1", force=True
        )
        chat.assert_called_once()
        cache_get_m.assert_called_once()
        cache_set_m.assert_called_once()

    def test_explain_real_error_not_skipped(self):
        """grep exit 2 (real error) is not skipped; normal flow runs."""
        _, chat, cache_set_m, cache_get_m = self._run_explain(
            "grep foo file", "grep: file: No such file or directory", "2"
        )
        chat.assert_called_once()
        cache_get_m.assert_called_once()
        cache_set_m.assert_called_once()

    def test_skip_notice_format(self):
        """Skip notice contains 'not an error' and 'nothing to explain'."""
        console, _, _, _ = self._run_explain("grep foo file", "", "1")
        calls_str = str(console.print.call_args_list)
        assert "not an error" in calls_str
        assert "nothing to explain" in calls_str
