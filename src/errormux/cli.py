"""CLI entry point for ErrorMux."""

from pathlib import Path

from rich.console import Console
import typer

from errormux.cache import cache_get, cache_set, make_cache_key
from errormux.client import chat_with_ollama
from errormux.parser import ParseError, parse_response
from errormux.prompts import SYSTEM_PROMPT, build_user_prompt

app = typer.Typer(
    name="errormux",
    help="On-demand shell command error explanations",
)

# Temp file paths (written by Phase 1 zsh plugin)
TEMP_CMD = Path("/tmp/shell-explainer-last-cmd")
TEMP_STDERR = Path("/tmp/shell-explainer-last-stderr")
TEMP_EXIT = Path("/tmp/shell-explainer-last-exit")


def read_context() -> tuple[str, str, int]:
    """Read captured command context from temp files.

    Returns:
        Tuple of (command, stderr, exit_code)

    Raises:
        FileNotFoundError: If temp files don't exist
    """
    cmd = TEMP_CMD.read_text().strip()
    stderr = TEMP_STDERR.read_text().strip()
    exit_code = int(TEMP_EXIT.read_text().strip())
    return cmd, stderr, exit_code


@app.command()
def explain() -> None:
    """Explain the last failed command.

    Reads captured command context from temp files, calls Ollama for
    AI-powered explanation, and displays formatted WHY/FIX output.
    """
    console = Console()

    try:
        cmd, stderr, exit_code = read_context()
    except FileNotFoundError:
        console.print("[errormux] No command captured")
        return

    cache_key = make_cache_key(cmd, stderr)
    cached_response = cache_get(cache_key)

    if cached_response:
        lines = cached_response.split("\n")
        for line in lines:
            if line.startswith("WHY:"):
                console.print(line, style="dim")
            elif line.startswith("FIX:"):
                console.print(line, style="bold green")
            else:
                console.print(line)
        return

    try:
        user_prompt = build_user_prompt(cmd, stderr, exit_code)
        response = chat_with_ollama(SYSTEM_PROMPT, user_prompt)

        try:
            why, fix = parse_response(response)
            console.print(f"WHY: {why}", style="dim")
            console.print(f"FIX: {fix}", style="bold green")
            cache_set(cache_key, f"WHY: {why}\nFIX: {fix}")
        except ParseError:
            console.print(response)

    except TimeoutError:
        console.print("[explainer offline]")
    except ConnectionError:
        console.print("[explainer offline]")


if __name__ == "__main__":
    app()
