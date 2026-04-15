"""Tests for Ollama client wrapper."""

import pytest
from unittest.mock import MagicMock, patch
from httpx import TimeoutException

from errormux.client import chat_with_ollama


class TestChatWithOllama:
    """Tests for chat_with_ollama function."""

    def test_returns_buffered_response_when_ollama_responds(self):
        """chat_with_ollama returns buffered response when Ollama responds."""
        mock_chunks = [
            {"message": {"content": "WHY: "}},
            {"message": {"content": "File not found."}},
            {"message": {"content": "\nFIX: "}},
            {"message": {"content": "touch myfile.txt"}},
        ]

        with patch("ollama.Client") as MockClient:
            mock_instance = MagicMock()
            MockClient.return_value = mock_instance
            mock_instance.chat.return_value = iter(mock_chunks)

            result = chat_with_ollama(
                system_prompt="You are a shell error explainer.",
                user_prompt="Command: cat myfile.txt\nExit code: 1",
            )

            assert result == "WHY: File not found.\nFIX: touch myfile.txt"

    def test_raises_timeout_error_after_10s_timeout(self):
        """chat_with_ollama raises TimeoutError after 10s timeout (per D-09)."""
        with patch("ollama.Client") as MockClient:
            mock_instance = MagicMock()
            MockClient.return_value = mock_instance
            mock_instance.chat.side_effect = TimeoutException("Request timed out")

            with pytest.raises(TimeoutError):
                chat_with_ollama(
                    system_prompt="You are a shell error explainer.",
                    user_prompt="Command: cat myfile.txt\nExit code: 1",
                )

    def test_handles_ollama_service_down_gracefully(self):
        """chat_with_ollama handles Ollama service down gracefully."""
        import ollama

        with patch("ollama.Client") as MockClient:
            mock_instance = MagicMock()
            MockClient.return_value = mock_instance
            mock_instance.chat.side_effect = ollama.ResponseError("Service unavailable")

            with pytest.raises(ConnectionError):
                chat_with_ollama(
                    system_prompt="You are a shell error explainer.",
                    user_prompt="Command: cat myfile.txt\nExit code: 1",
                )

    def test_streams_response_and_buffers_full_text(self):
        """chat_with_ollama streams response and buffers full text (per D-04, D-05)."""
        mock_chunks = [
            {"message": {"content": "First "}},
            {"message": {"content": "Second "}},
            {"message": {"content": "Third"}},
        ]

        with patch("ollama.Client") as MockClient:
            mock_instance = MagicMock()
            MockClient.return_value = mock_instance
            mock_instance.chat.return_value = iter(mock_chunks)

            result = chat_with_ollama(
                system_prompt="System prompt",
                user_prompt="User prompt",
            )

            assert result == "First Second Third"

    def test_client_created_with_correct_host_and_timeout(self):
        """Client is created with correct host and timeout settings."""
        with patch("ollama.Client") as MockClient:
            mock_instance = MagicMock()
            MockClient.return_value = mock_instance
            mock_instance.chat.return_value = iter([])

            chat_with_ollama("system", "user")

            MockClient.assert_called_once_with(
                host="http://localhost:11434", timeout=10.0
            )

    def test_chat_called_with_correct_model_and_messages(self):
        """chat() is called with correct model and message format."""
        mock_chunks = [{"message": {"content": "response"}}]

        with patch("ollama.Client") as MockClient:
            mock_instance = MagicMock()
            MockClient.return_value = mock_instance
            mock_instance.chat.return_value = iter(mock_chunks)

            chat_with_ollama(
                system_prompt="System prompt here",
                user_prompt="User prompt here",
            )

            mock_instance.chat.assert_called_once()
            call_kwargs = mock_instance.chat.call_args.kwargs
            assert call_kwargs["model"] == "gemma3:4b"
            assert call_kwargs["stream"] is True
            assert call_kwargs["messages"] == [
                {"role": "system", "content": "System prompt here"},
                {"role": "user", "content": "User prompt here"},
            ]
