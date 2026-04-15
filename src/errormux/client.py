"""Ollama client wrapper with streaming and error handling."""

from httpx import TimeoutException

import ollama

# Constants per project constraints and D-09
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_TIMEOUT = 10.0  # 10s timeout per D-09
OLLAMA_MODEL = "gemma3:4b"  # Project constraint


def chat_with_ollama(system_prompt: str, user_prompt: str) -> str:
    """Stream from Ollama, return buffered response.

    Args:
        system_prompt: System message for the LLM
        user_prompt: User message with command context

    Returns:
        Buffered response text from Ollama

    Raises:
        TimeoutError: If Ollama request times out (10s)
        ConnectionError: If Ollama service is unavailable
    """
    client = ollama.Client(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT)

    try:
        # Stream response and buffer full text (per D-04, D-05)
        response_text = ""
        for chunk in client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
        ):
            response_text += chunk["message"]["content"]
        return response_text

    except TimeoutException as e:
        # Re-raise as TimeoutError for cleaner interface
        raise TimeoutError(f"Ollama request timed out: {e}") from e

    except ollama.ResponseError as e:
        # Re-raise as ConnectionError for service-down scenarios
        raise ConnectionError(f"Ollama service unavailable: {e}") from e
