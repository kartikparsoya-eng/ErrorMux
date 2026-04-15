"""Prompt construction for shell error explanation."""

# System prompt per D-01, D-02, D-03
SYSTEM_PROMPT = """You are a shell error explainer for zsh.
Given a failed command, stderr, and exit code, explain briefly.

Output format (REQUIRED):
WHY: <one sentence explanation of what went wrong>
FIX: <the command to fix it>

Keep WHY to one sentence. FIX should be a valid shell command.
Do not include any other text or explanation."""


def build_user_prompt(cmd: str, stderr: str, exit_code: int) -> str:
    """Build user prompt from command context.

    Args:
        cmd: The failed command
        stderr: Stderr output from the command
        exit_code: Exit code of the command

    Returns:
        Formatted user prompt string
    """
    return f"""Command: {cmd}
Exit code: {exit_code}
Stderr: {stderr}

Explain this error."""
