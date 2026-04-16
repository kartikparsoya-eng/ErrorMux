"""Ollama client wrapper with streaming and error handling."""

from httpx import ConnectError, TimeoutException

import ollama

from errormux.config import get_model_name

# Constants per project constraints and D-09
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_TIMEOUT = 10.0  # 10s timeout per D-09


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
        RuntimeError: If model not found
    """
    client = ollama.Client(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT)
    model = get_model_name()

    try:
        # Stream response and buffer full text (per D-04, D-05)
        response_text = ""
        for chunk in client.chat(
            model=model,
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

    except ConnectError as e:
        # Re-raise as ConnectionError for service-down scenarios
        raise ConnectionError("Ollama service unavailable") from e

    except ollama.ResponseError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "model" in error_msg:
            raise RuntimeError(
                f"Model {model} not found.\nRun: ollama pull {model}"
            ) from e
        raise ConnectionError(f"Ollama error: {e}") from e
