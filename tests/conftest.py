"""Shared test fixtures for ErrorMux tests."""

import httpx
import json
from contextlib import contextmanager
from unittest.mock import patch


@contextmanager
def mock_ollama_streaming(content="WHY: test\nFIX: test fix"):
    """
    Mock Ollama chat API using httpx.MockTransport.
    Simulates streaming response from ollama SDK.

    Args:
        content: The content to return in the response

    Yields:
        The expected content (for assertion convenience)
    """

    def handler(request):
        # ollama SDK sends POST to /api/chat with JSON body
        # Simulate streaming response - ollama returns JSON lines
        # Each response must have 'message' with 'role' and 'content'
        # The final response has 'done': true
        chunks = [
            {"message": {"role": "assistant", "content": content}, "done": False},
            {"message": {"role": "assistant", "content": ""}, "done": True},
        ]

        def content_gen():
            for chunk in chunks:
                yield (json.dumps(chunk) + "\n").encode()

        return httpx.Response(200, content=content_gen())

    transport = httpx.MockTransport(handler)
    mock_client = httpx.Client(transport=transport, base_url="http://localhost:11434")

    # Patch httpx.Client to return our mock when ollama creates its internal client
    with patch("httpx.Client", return_value=mock_client):
        yield content
