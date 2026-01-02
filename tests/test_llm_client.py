"""Tests for LLM client factory (FND-02)."""

import pytest
from unittest.mock import patch, MagicMock


class TestCreateLLM:
    """Tests for create_llm() factory function."""

    def test_create_openai_client(self, temp_env_file):
        """Test that OpenAI provider creates ChatOpenAI instance."""
        # Need to mock settings before importing llm_client
        with patch.dict("sys.modules", {"src.config": MagicMock()}):
            import sys

            # Create mock settings
            mock_settings = MagicMock()
            mock_settings.llm_provider = "openai"
            mock_settings.llm_model = "gpt-4o-mini"
            mock_settings.openai_api_key = "test-openai-key"

            sys.modules["src.config"].settings = mock_settings

            # Now import create_llm - it will use our mocked settings
            from src.llm_client import create_llm
            from langchain_openai import ChatOpenAI

            client = create_llm()

            assert isinstance(client, ChatOpenAI)
            assert client.model_name == "gpt-4o-mini"

    def test_create_claude_client(self, temp_env_file):
        """Test that Claude provider creates ChatAnthropic instance."""
        with patch.dict("sys.modules", {"src.config": MagicMock()}):
            import sys

            mock_settings = MagicMock()
            mock_settings.llm_provider = "claude"
            mock_settings.llm_model = "claude-3-5-sonnet-latest"
            mock_settings.anthropic_api_key = "test-anthropic-key"

            sys.modules["src.config"].settings = mock_settings

            # Reimport to pick up new mock
            import importlib
            import src.llm_client

            importlib.reload(src.llm_client)
            from src.llm_client import create_llm
            from langchain_anthropic import ChatAnthropic

            client = create_llm()

            assert isinstance(client, ChatAnthropic)
            assert client.model == "claude-3-5-sonnet-latest"

    def test_create_deepseek_client(self, temp_env_file):
        """Test that DeepSeek provider creates ChatDeepSeek instance."""
        with patch.dict("sys.modules", {"src.config": MagicMock()}):
            import sys

            mock_settings = MagicMock()
            mock_settings.llm_provider = "deepseek"
            mock_settings.llm_model = "deepseek-chat"
            mock_settings.deepseek_api_key = "test-deepseek-key"

            sys.modules["src.config"].settings = mock_settings

            # Reimport to pick up new mock
            import importlib
            import src.llm_client

            importlib.reload(src.llm_client)
            from src.llm_client import create_llm
            from langchain_deepseek import ChatDeepSeek

            client = create_llm()

            assert isinstance(client, ChatDeepSeek)
            assert client.model_name == "deepseek-chat"

    def test_invalid_provider_raises(self, temp_env_file):
        """Test that invalid provider raises ValueError."""
        with patch.dict("sys.modules", {"src.config": MagicMock()}):
            import sys

            mock_settings = MagicMock()
            mock_settings.llm_provider = "invalid_provider"
            mock_settings.llm_model = "some-model"

            sys.modules["src.config"].settings = mock_settings

            # Reimport to pick up new mock
            import importlib
            import src.llm_client

            importlib.reload(src.llm_client)
            from src.llm_client import create_llm

            with pytest.raises(ValueError, match="Unsupported provider"):
                create_llm()


class TestCreateLLMWithTemp:
    """Tests for create_llm_with_temp() factory function."""

    def test_create_openai_with_temperature(self, temp_env_file):
        """Test that temperature is passed to OpenAI client."""
        with patch.dict("sys.modules", {"src.config": MagicMock()}):
            import sys

            mock_settings = MagicMock()
            mock_settings.llm_provider = "openai"
            mock_settings.llm_model = "gpt-4o-mini"
            mock_settings.openai_api_key = "test-openai-key"

            sys.modules["src.config"].settings = mock_settings

            import importlib
            import src.llm_client

            importlib.reload(src.llm_client)
            from src.llm_client import create_llm_with_temp
            from langchain_openai import ChatOpenAI

            client = create_llm_with_temp(temperature=0.5)

            assert isinstance(client, ChatOpenAI)
            assert client.model_name == "gpt-4o-mini"
            assert client.temperature == 0.5

    def test_create_claude_with_temperature(self, temp_env_file):
        """Test that temperature is passed to Claude client."""
        with patch.dict("sys.modules", {"src.config": MagicMock()}):
            import sys

            mock_settings = MagicMock()
            mock_settings.llm_provider = "claude"
            mock_settings.llm_model = "claude-3-5-sonnet-latest"
            mock_settings.anthropic_api_key = "test-anthropic-key"

            sys.modules["src.config"].settings = mock_settings

            import importlib
            import src.llm_client

            importlib.reload(src.llm_client)
            from src.llm_client import create_llm_with_temp
            from langchain_anthropic import ChatAnthropic

            client = create_llm_with_temp(temperature=0.2)

            assert isinstance(client, ChatAnthropic)
            assert client.model == "claude-3-5-sonnet-latest"
            assert client.temperature == 0.2

    def test_create_deepseek_with_temperature(self, temp_env_file):
        """Test that temperature is passed to DeepSeek client."""
        with patch.dict("sys.modules", {"src.config": MagicMock()}):
            import sys

            mock_settings = MagicMock()
            mock_settings.llm_provider = "deepseek"
            mock_settings.llm_model = "deepseek-chat"
            mock_settings.deepseek_api_key = "test-deepseek-key"

            sys.modules["src.config"].settings = mock_settings

            import importlib
            import src.llm_client

            importlib.reload(src.llm_client)
            from src.llm_client import create_llm_with_temp
            from langchain_deepseek import ChatDeepSeek

            client = create_llm_with_temp(temperature=0.1)

            assert isinstance(client, ChatDeepSeek)
            assert client.model_name == "deepseek-chat"
            assert client.temperature == 0.1

    def test_default_temperature_is_zero(self, temp_env_file):
        """Test that default temperature is 0.0."""
        with patch.dict("sys.modules", {"src.config": MagicMock()}):
            import sys

            mock_settings = MagicMock()
            mock_settings.llm_provider = "openai"
            mock_settings.llm_model = "gpt-4o-mini"
            mock_settings.openai_api_key = "test-openai-key"

            sys.modules["src.config"].settings = mock_settings

            import importlib
            import src.llm_client

            importlib.reload(src.llm_client)
            from src.llm_client import create_llm_with_temp

            client = create_llm_with_temp()

            assert client.temperature == 0.0
