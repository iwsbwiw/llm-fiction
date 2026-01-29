"""Tests for StoryStore.list_stories() method (UI-04, UI-06)."""
from datetime import datetime
from pathlib import Path

import pytest

from src.models import Character, CharacterType, Chapter, Novel, NovelStatus
from src.storage import StoryStore


class TestListStories:
    """Tests for StoryStore.list_stories() method."""

    @pytest.fixture
    def store(self, tmp_path: Path) -> StoryStore:
        """Create StoryStore with temporary directory.

        Args:
            tmp_path: pytest's built-in temporary directory fixture.

        Returns:
            StoryStore instance using temp directory.
        """
        return StoryStore(base_dir=tmp_path / "stories")

    @pytest.fixture
    def sample_novel(self) -> Novel:
        """Create sample Novel for testing.

        Returns:
            Novel instance with test data.
        """
        return Novel(
            title="Test Novel",
            one_sentence_prompt="A hero saves the world.",
            genre="Fantasy",
            style_tags=["epic", "adventure"],
        )

    @pytest.fixture
    def sample_chapters(self) -> list[Chapter]:
        """Create sample Chapters for testing.

        Returns:
            List of Chapter instances.
        """
        return [
            Chapter(
                title="Chapter 1: The Beginning",
                content="Once upon a time in a distant land...",
                chapter_number=1,
                plot_points=["Hero introduced", "Quest begins"],
            ),
            Chapter(
                title="Chapter 2: The Journey",
                content="The hero embarked on a long journey...",
                chapter_number=2,
                plot_points=["First challenge", "New ally met"],
            ),
        ]

    @pytest.fixture
    def sample_characters(self) -> list[Character]:
        """Create sample Characters for testing.

        Returns:
            List of Character instances.
        """
        return [
            Character(
                name="Alice",
                description="The brave hero",
                character_type=CharacterType.PROTAGONIST,
                personality="Courageous and kind",
            ),
        ]

    def test_list_stories_method_exists(self, store: StoryStore):
        """Test 1: list_stories method exists on StoryStore."""
        assert hasattr(store, "list_stories")
        assert callable(getattr(store, "list_stories"))

    def test_list_stories_returns_list_of_dicts_with_keys(
        self,
        store: StoryStore,
        sample_novel: Novel,
        sample_chapters: list[Chapter],
        sample_characters: list[Character],
    ):
        """Test 2: Returns list of dicts with id, title, chapter_count keys."""
        store.save(sample_novel, sample_chapters, sample_characters)
        stories = store.list_stories()

        assert isinstance(stories, list)
        assert len(stories) == 1

        story = stories[0]
        assert "id" in story
        assert "title" in story
        assert "chapter_count" in story
        assert story["title"] == sample_novel.title
        assert story["chapter_count"] == len(sample_chapters)

    def test_list_stories_returns_empty_list_when_no_stories(
        self,
        store: StoryStore,
    ):
        """Test 3: Returns empty list when no stories exist."""
        stories = store.list_stories()

        assert isinstance(stories, list)
        assert len(stories) == 0

    def test_list_stories_skips_corrupted_json_files(
        self,
        store: StoryStore,
        sample_novel: Novel,
        sample_chapters: list[Chapter],
        sample_characters: list[Character],
    ):
        """Test 4: Skips corrupted JSON files without raising."""
        # Save a valid story
        valid_id = store.save(sample_novel, sample_chapters, sample_characters)

        # Create a corrupted JSON file
        corrupted_path = store.base_dir / "corrupted-file.json"
        corrupted_path.write_text("{ not valid json", encoding="utf-8")

        # list_stories should skip the corrupted file and return only valid stories
        stories = store.list_stories()

        assert len(stories) == 1
        assert stories[0]["id"] == valid_id

    def test_list_stories_sorts_by_created_at_descending(
        self,
        store: StoryStore,
        sample_chapters: list[Chapter],
        sample_characters: list[Character],
    ):
        """Test 5: Stories sorted by created_at descending (newest first)."""
        # Create novels with different created_at times and unique IDs
        novel1 = Novel(
            id="20250101-100000",
            title="Older Story",
            one_sentence_prompt="First story.",
            created_at=datetime(2025, 1, 1, 10, 0, 0),
        )
        novel2 = Novel(
            id="20251231-100000",
            title="Newer Story",
            one_sentence_prompt="Second story.",
            created_at=datetime(2025, 12, 31, 10, 0, 0),
        )
        novel3 = Novel(
            id="20250615-100000",
            title="Middle Story",
            one_sentence_prompt="Third story.",
            created_at=datetime(2025, 6, 15, 10, 0, 0),
        )

        store.save(novel1, sample_chapters, sample_characters)
        store.save(novel2, sample_chapters, sample_characters)
        store.save(novel3, sample_chapters, sample_characters)

        stories = store.list_stories()

        # Should be sorted: newest first
        assert len(stories) == 3
        assert stories[0]["title"] == "Newer Story"
        assert stories[1]["title"] == "Middle Story"
        assert stories[2]["title"] == "Older Story"

    def test_list_stories_includes_last_read_chapter(
        self,
        store: StoryStore,
        sample_chapters: list[Chapter],
        sample_characters: list[Character],
    ):
        """Test 6: list_stories includes last_read_chapter in result."""
        novel = Novel(
            title="Story with Progress",
            one_sentence_prompt="A story.",
            last_read_chapter=2,
        )

        store.save(novel, sample_chapters, sample_characters)
        stories = store.list_stories()

        assert len(stories) == 1
        assert "last_read_chapter" in stories[0]
        assert stories[0]["last_read_chapter"] == 2
