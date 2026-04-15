"""Tests for CLI explain command."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os

from errormux.cli import explain, read_context


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
