"""Tests for StoryBible and ChapterSummary models (MEM-01, MEM-02)."""

import pytest

from src.memory import ChapterSummary, StoryBible


class TestStoryBibleModel:
    """Tests for StoryBible model structure."""

    def test_story_bible_has_all_tiers(self):
        """Verify StoryBible has all 4 tier fields."""
        bible = StoryBible()

        assert hasattr(bible, "recent_chapters")
        assert hasattr(bible, "short_term_arc")
        assert hasattr(bible, "long_term_macro")
        assert hasattr(bible, "characters")

    def test_story_bible_defaults(self):
        """Verify StoryBible default values."""
        bible = StoryBible()

        assert bible.recent_chapters == []
        assert bible.short_term_arc == []
        assert bible.long_term_macro is None
        assert bible.characters == []

    def test_story_bible_with_values(self):
        """Verify StoryBible accepts all tier values."""
        from src.models import Chapter, Character, CharacterType

        chapter = Chapter(title="Ch1", content="Content", chapter_number=1)
        summary = ChapterSummary(chapter_number=1, summary="A test summary")
        character = Character(
            name="Hero",
            description="Main character",
            character_type=CharacterType.PROTAGONIST,
        )

        bible = StoryBible(
            recent_chapters=[chapter],
            short_term_arc=[summary],
            long_term_macro="An epic adventure",
            characters=[character],
        )

        assert len(bible.recent_chapters) == 1
        assert len(bible.short_term_arc) == 1
        assert bible.long_term_macro == "An epic adventure"
        assert len(bible.characters) == 1


class TestChapterSummaryModel:
    """Tests for ChapterSummary model."""

    def test_chapter_summary_fields(self):
        """Verify ChapterSummary has required fields."""
        summary = ChapterSummary(
            chapter_number=1,
            summary="Hero meets the villain.",
        )

        assert summary.chapter_number == 1
        assert summary.summary == "Hero meets the villain."
        assert summary.key_plot_points == []

    def test_chapter_summary_with_plot_points(self):
        """Verify ChapterSummary accepts key_plot_points."""
        summary = ChapterSummary(
            chapter_number=5,
            summary="The climax approaches.",
            key_plot_points=["Hero finds sword", "Villain reveals plan"],
        )

        assert summary.chapter_number == 5
        assert len(summary.key_plot_points) == 2
        assert "Hero finds sword" in summary.key_plot_points

    def test_chapter_summary_serialization(self):
        """Verify ChapterSummary can be serialized and restored."""
        summary = ChapterSummary(
            chapter_number=3,
            summary="A turning point.",
            key_plot_points=["Decision made"],
        )

        data = summary.model_dump()
        restored = ChapterSummary.model_validate(data)

        assert restored.chapter_number == summary.chapter_number
        assert restored.summary == summary.summary
        assert restored.key_plot_points == summary.key_plot_points
