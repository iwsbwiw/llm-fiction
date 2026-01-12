"""Tests for memory tier limit enforcement (D-01, D-02, D-03, D-04)."""

import pytest

from src.memory import ChapterSummary, StoryBible
from src.memory.story_bible import StoryBibleManager


class TestL1TierLimit:
    """Tests for L1 (recent_chapters) max 2 limit per D-01."""

    def test_l1_max_2_chapters(self, sample_chapter):
        """Add 3 chapters, verify only last 2 remain."""
        manager = StoryBibleManager()

        # Add 3 chapters
        for i in range(1, 4):
            from src.models import Chapter

            chapter = Chapter(
                title=f"Chapter {i}",
                content=f"Content {i}",
                chapter_number=i,
            )
            manager.add_chapter(chapter)

        bible = manager.get_context()
        assert len(bible.recent_chapters) == 2
        assert bible.recent_chapters[0].chapter_number == 2
        assert bible.recent_chapters[1].chapter_number == 3

    def test_l1_keeps_most_recent(self, sample_chapter):
        """Verify L1 keeps the most recent chapters."""
        manager = StoryBibleManager()

        for i in range(1, 6):
            from src.models import Chapter

            chapter = Chapter(
                title=f"Chapter {i}",
                content=f"Content {i}",
                chapter_number=i,
            )
            manager.add_chapter(chapter)

        bible = manager.get_context()
        assert bible.recent_chapters[0].chapter_number == 4
        assert bible.recent_chapters[1].chapter_number == 5


class TestL2TierLimit:
    """Tests for L2 (short_term_arc) max 5 limit per D-02."""

    def test_l2_max_5_summaries(self):
        """Add 6 summaries, verify only last 5 remain."""
        manager = StoryBibleManager()

        # Add 6 summaries
        for i in range(1, 7):
            summary = ChapterSummary(
                chapter_number=i,
                summary=f"Summary for chapter {i}",
            )
            manager.add_summary(summary)

        bible = manager.get_context()
        assert len(bible.short_term_arc) == 5
        # Should keep chapters 2-6
        chapter_numbers = [s.chapter_number for s in bible.short_term_arc]
        assert chapter_numbers == [2, 3, 4, 5, 6]

    def test_l2_keeps_most_recent(self):
        """Verify L2 keeps the most recent summaries."""
        manager = StoryBibleManager()

        for i in range(1, 12):
            summary = ChapterSummary(
                chapter_number=i,
                summary=f"Summary {i}",
            )
            manager.add_summary(summary)

        bible = manager.get_context()
        assert len(bible.short_term_arc) == 5
        chapter_numbers = [s.chapter_number for s in bible.short_term_arc]
        assert chapter_numbers == [7, 8, 9, 10, 11]


class TestL3Macro:
    """Tests for L3 (long_term_macro) per D-03."""

    def test_l3_update_macro(self):
        """Call update_macro(), verify field updated."""
        manager = StoryBibleManager()

        manager.update_macro("A hero's journey through dark lands.")

        bible = manager.get_context()
        assert bible.long_term_macro == "A hero's journey through dark lands."

    def test_l3_can_be_updated(self):
        """Verify macro can be updated multiple times."""
        manager = StoryBibleManager()

        manager.update_macro("First version")
        manager.update_macro("Updated version")

        bible = manager.get_context()
        assert bible.long_term_macro == "Updated version"


class TestL4Characters:
    """Tests for L4 (characters) entity registry per D-04."""

    def test_l4_add_character(self, sample_character):
        """Add character, verify in characters list."""
        manager = StoryBibleManager()

        manager.add_character(sample_character)

        bible = manager.get_context()
        assert len(bible.characters) == 1
        assert bible.characters[0].name == "Alice"

    def test_l4_multiple_characters(self, sample_character):
        """Verify multiple characters can be added."""
        from src.models import Character, CharacterType

        manager = StoryBibleManager()

        manager.add_character(sample_character)

        sidekick = Character(
            name="Bob",
            description="Loyal friend",
            character_type=CharacterType.SUPPORTING,
        )
        manager.add_character(sidekick)

        bible = manager.get_context()
        assert len(bible.characters) == 2
        names = [c.name for c in bible.characters]
        assert "Alice" in names
        assert "Bob" in names


class TestStoryBibleManagerInit:
    """Tests for StoryBibleManager initialization."""

    def test_init_creates_default_bible(self):
        """Verify manager creates empty StoryBible by default."""
        manager = StoryBibleManager()

        bible = manager.get_context()
        assert isinstance(bible, StoryBible)
        assert bible.recent_chapters == []

    def test_init_accepts_existing_bible(self, sample_story_bible):
        """Verify manager can wrap existing StoryBible."""
        manager = StoryBibleManager(story_bible=sample_story_bible)

        bible = manager.get_context()
        assert bible is sample_story_bible
