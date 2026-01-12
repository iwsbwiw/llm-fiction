"""Shared pytest fixtures for configuration tests."""

import os
import pytest
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_env_file(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary .env file with test values.

    Args:
        tmp_path: pytest's built-in temporary directory fixture.

    Yields:
        Path to the temporary .env file.
    """
    env_file = tmp_path / ".env"
    env_file.write_text(
        "LLM_PROVIDER=openai\n"
        "OPENAI_API_KEY=test-openai-key\n"
        "LLM_MODEL=gpt-4o-mini\n"
        "CHAPTER_LENGTH=2000\n",
        encoding="utf-8",
    )
    yield env_file


@pytest.fixture
def sample_settings(temp_env_file: Path):
    """Create a Settings instance with test configuration.

    Args:
        temp_env_file: Path to temporary .env file.

    Returns:
        Settings instance configured for testing.
    """
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from typing import Literal

    class TestSettings(BaseSettings):
        model_config = SettingsConfigDict(
            env_file=str(temp_env_file),
            env_file_encoding="utf-8",
            case_sensitive=False,
            extra="ignore",
        )

        llm_provider: Literal["openai", "claude", "deepseek"] = "openai"
        llm_model: str = "gpt-4o-mini"
        chapter_length: int = 2000
        data_dir: str = "data/stories"

        openai_api_key: str | None = None
        anthropic_api_key: str | None = None
        deepseek_api_key: str | None = None

        def validate_provider_key(self) -> None:
            key_map = {
                "openai": self.openai_api_key,
                "claude": self.anthropic_api_key,
                "deepseek": self.deepseek_api_key,
            }
            if not key_map.get(self.llm_provider):
                raise ValueError(f"API key required for provider: {self.llm_provider}")

    return TestSettings()


@pytest.fixture
def sample_chapter():
    """Create a sample Chapter for testing."""
    from src.models import Chapter

    return Chapter(
        title="Test Chapter",
        content="Test content for the chapter.",
        chapter_number=1,
    )


@pytest.fixture
def sample_character():
    """Create a sample Character for testing."""
    from src.models import Character, CharacterType

    return Character(
        name="Alice",
        description="A brave explorer",
        character_type=CharacterType.PROTAGONIST,
        personality="Courageous and curious",
    )


@pytest.fixture
def sample_story_bible():
    """Create a sample StoryBible for testing."""
    from src.memory import StoryBible

    return StoryBible()


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing without API calls."""
    from unittest.mock import MagicMock
    from src.memory.models import ExtractionResult

    mock = MagicMock()
    mock_result = ExtractionResult(
        plot_developments=["Hero finds a map"],
        character_updates={"Alice": "Discovered hidden power"},
        world_building_updates="Ancient temple revealed",
        summary="Alice discovers her hidden power while exploring an ancient temple."
    )

    mock_extractor = MagicMock()
    mock_extractor.invoke.return_value = mock_result
    mock.with_structured_output.return_value = mock_extractor

    return mock


@pytest.fixture
def mock_create_llm_with_temp():
    """Create a mock for create_llm_with_temp function."""
    from unittest.mock import MagicMock

    def _create_mock(temperature: float):
        mock = MagicMock()
        mock.temperature = temperature
        return mock

    return _create_mock


class MockSessionState(dict):
    """Mock Streamlit session_state for unit tests.

    Provides dict-like operations plus dot notation access to mimic
    st.session_state behavior in tests.

    Example:
        state = MockSessionState()
        state.app_state = "input"  # dot notation
        if "app_state" not in state:  # dict-like check
            state["app_state"] = "input"
    """

    def __getattr__(self, name: str):
        """Allow dot notation access to session state items."""
        try:
            return self[name]
        except KeyError:
            raise AttributeError(f"MockSessionState has no attribute '{name}'")

    def __setattr__(self, name: str, value) -> None:
        """Allow dot notation assignment to session state items."""
        self[name] = value


@pytest.fixture
def mock_session_state():
    """Create a fresh MockSessionState instance for testing.

    Returns:
        MockSessionState: A dict-like object that supports dot notation.
    """
    return MockSessionState()

