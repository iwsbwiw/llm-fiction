"""Tests for Pydantic data models (FND-04)."""
import pytest
from datetime import datetime

from src.models import Novel, NovelStatus, Chapter, Character, CharacterType


class TestNovelModel:
    """Tests for Novel model."""

    def test_novel_model(self):
        """Create Novel with required fields, verify defaults applied."""
        novel = Novel(
            title="Test Novel",
            one_sentence_prompt="A hero saves the world.",
        )

        assert novel.title == "Test Novel"
        assert novel.one_sentence_prompt == "A hero saves the world."
        assert novel.status == NovelStatus.DRAFT
        assert novel.genre is None
        assert novel.style_tags == []
        assert novel.target_chapters == 10
        assert novel.outline is None
        assert novel.world_building is None
        assert novel.main_arc is None
        assert novel.user_rating is None
        assert novel.is_favorite is False
        assert novel.last_read_chapter == 0
        assert isinstance(novel.created_at, datetime)

    def test_novel_rating_validation(self):
        """user_rating rejects values outside 1-5."""
        # Valid ratings
        for rating in [1, 3, 5]:
            novel = Novel(
                title="Test",
                one_sentence_prompt="Test",
                user_rating=rating,
            )
            assert novel.user_rating == rating

        # Invalid ratings
        with pytest.raises(Exception):  # ValidationError
            Novel(
                title="Test",
                one_sentence_prompt="Test",
                user_rating=0,
            )

        with pytest.raises(Exception):  # ValidationError
            Novel(
                title="Test",
                one_sentence_prompt="Test",
                user_rating=6,
            )

    def test_novel_serialization(self):
        """model_dump() produces valid JSON-serializable dict."""
        novel = Novel(
            title="Test Novel",
            one_sentence_prompt="A hero saves the world.",
            genre="Fantasy",
            style_tags=["epic", "dark"],
        )

        data = novel.model_dump()

        assert isinstance(data, dict)
        assert data["title"] == "Test Novel"
        assert data["genre"] == "Fantasy"
        assert data["style_tags"] == ["epic", "dark"]
        assert data["status"] == NovelStatus.DRAFT

        # Verify it can be validated back
        restored = Novel.model_validate(data)
        assert restored.title == novel.title
        assert restored.genre == novel.genre


class TestChapterModel:
    """Tests for Chapter model."""

    def test_chapter_model(self):
        """Create Chapter with required fields, verify defaults."""
        chapter = Chapter(
            title="Chapter 1",
            content="Once upon a time...",
            chapter_number=1,
        )

        assert chapter.title == "Chapter 1"
        assert chapter.content == "Once upon a time..."
        assert chapter.chapter_number == 1
        assert chapter.chapter_outline is None
        assert chapter.plot_points == []
        assert chapter.character_appearances == []
        assert chapter.is_read is False
        assert chapter.read_at is None
        assert isinstance(chapter.generated_at, datetime)

    def test_chapter_serialization(self):
        """model_dump() and model_validate() roundtrip."""
        chapter = Chapter(
            title="Chapter 1",
            content="The story begins...",
            chapter_number=1,
            plot_points=["Hero introduced", "Villain revealed"],
            is_read=True,
        )

        data = chapter.model_dump()
        restored = Chapter.model_validate(data)

        assert restored.title == chapter.title
        assert restored.content == chapter.content
        assert restored.chapter_number == chapter.chapter_number
        assert restored.plot_points == chapter.plot_points
        assert restored.is_read == chapter.is_read


class TestCharacterModel:
    """Tests for Character model."""

    def test_character_model(self):
        """Create Character with required fields, verify enum works."""
        character = Character(
            name="Alice",
            description="The brave hero",
            character_type=CharacterType.PROTAGONIST,
        )

        assert character.name == "Alice"
        assert character.description == "The brave hero"
        assert character.character_type == CharacterType.PROTAGONIST
        assert character.personality is None
        assert character.backstory is None
        assert character.motivations is None
        assert character.relationships == []
        assert character.development_arc is None

    def test_character_type_enum(self):
        """CharacterType has PROTAGONIST and SUPPORTING values."""
        assert CharacterType.PROTAGONIST.value == "protagonist"
        assert CharacterType.SUPPORTING.value == "supporting"

        # Test enum usage
        hero = Character(
            name="Hero",
            description="Main character",
            character_type=CharacterType.PROTAGONIST,
        )
        assert hero.character_type == CharacterType.PROTAGONIST

        sidekick = Character(
            name="Sidekick",
            description="Supporting character",
            character_type=CharacterType.SUPPORTING,
        )
        assert sidekick.character_type == CharacterType.SUPPORTING
