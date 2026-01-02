"""Tests for agent nodes (AGT-01, AGT-02, AGT-03, D-13, D-14)."""

import pytest
from unittest.mock import MagicMock, patch

from src.agents.schemas import ChapterOutline, ReviewResult, StoryInitialization
from src.memory.models import StoryBible


class TestInitializeStoryNode:
    """Tests for initialize_story_node function."""

    def test_initialize_story(self, sample_story_bible):
        """Test that initialize_story_node creates StoryBible from one-liner."""
        from src.agents.nodes import initialize_story_node

        mock_result = StoryInitialization(
            title="The Great Adventure",
            genre="fantasy",
            main_characters=["Alice", "Bob", "Charlie"],
            story_arc="A hero's journey to save the world from an ancient evil",
            initial_outline=[]
        )

        with patch("src.agents.nodes.create_llm_with_temp") as mock_create_llm:
            mock_llm = MagicMock()
            mock_structured = MagicMock()
            mock_structured.invoke.return_value = mock_result
            mock_llm.with_structured_output.return_value = mock_structured
            mock_create_llm.return_value = mock_llm

            state = {"user_prompt": "A detective in Shanghai"}

            result = initialize_story_node(state)

            assert "story_bible" in result
            story_bible = result["story_bible"]
            assert story_bible.long_term_macro == "A hero's journey to save the world from an ancient evil"
            assert len(story_bible.characters) == 3
            assert story_bible.characters[0].name == "Alice"
            assert story_bible.characters[0].character_type.value == "protagonist"
            assert story_bible.characters[1].character_type.value == "supporting"
            mock_create_llm.assert_called_once_with(temperature=0.3)

    def test_initialize_story_uses_structured_output(self, sample_story_bible):
        """Test that initialize_story_node uses with_structured_output(StoryInitialization)."""
        from src.agents.nodes import initialize_story_node

        with patch("src.agents.nodes.create_llm_with_temp") as mock_create_llm:
            mock_llm = MagicMock()
            mock_structured = MagicMock()
            mock_structured.invoke.return_value = StoryInitialization(
                title="Test",
                genre="test",
                main_characters=["Test"],
                story_arc="Test arc",
                initial_outline=[]
            )
            mock_llm.with_structured_output.return_value = mock_structured
            mock_create_llm.return_value = mock_llm

            state = {"user_prompt": "Test prompt"}

            initialize_story_node(state)

            mock_llm.with_structured_output.assert_called_once_with(StoryInitialization)
