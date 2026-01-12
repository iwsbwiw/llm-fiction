"""Tests for context injection system per D-05, D-06."""

import pytest

from src.memory import StoryBible, ChapterSummary
from src.memory.context_injector import (
    inject_context,
    format_context,
    _format_l3_macro,
    _format_l2_arc,
    _format_l1_recent,
    _format_l4_characters,
    STORY_CONTEXT_TEMPLATE,
)
from src.models import Chapter, Character, CharacterType


class TestContextInjection:
    """Tests for context injection functions."""

    def test_inject_context_returns_messages(self, sample_story_bible):
        """inject_context returns list of 2 messages (system + human)."""
        messages = inject_context(sample_story_bible, "Write chapter 2")
        assert isinstance(messages, list)
        assert len(messages) == 2  # system + human

    def test_inject_context_message_types(self, sample_story_bible):
        """inject_context returns proper LangChain message types."""
        messages = inject_context(sample_story_bible, "Write chapter 2")
        # LangChain messages have a 'type' attribute
        assert hasattr(messages[0], "type") or hasattr(messages[0], "content")
        assert hasattr(messages[1], "type") or hasattr(messages[1], "content")

    def test_format_context_has_all_tiers(self, sample_story_bible):
        """format_context returns dict with all 4 tier keys."""
        ctx = format_context(sample_story_bible)
        assert "story_overview" in ctx
        assert "recent_developments" in ctx
        assert "latest_chapters" in ctx
        assert "active_characters" in ctx

    def test_format_context_returns_strings(self, sample_story_bible):
        """format_context returns string values for each tier."""
        ctx = format_context(sample_story_bible)
        assert isinstance(ctx["story_overview"], str)
        assert isinstance(ctx["recent_developments"], str)
        assert isinstance(ctx["latest_chapters"], str)
        assert isinstance(ctx["active_characters"], str)


class TestL3MacroFormatting:
    """Tests for L3 long-term macro formatting."""

    def test_l3_macro_shows_value(self, sample_story_bible):
        """L3 formatting shows macro when set."""
        sample_story_bible.long_term_macro = "Epic adventure across the cosmos"
        result = _format_l3_macro(sample_story_bible)
        assert "Epic adventure" in result

    def test_l3_macro_shows_fallback(self, sample_story_bible):
        """L3 formatting shows fallback when empty."""
        result = _format_l3_macro(sample_story_bible)
        assert "new story" in result.lower()


class TestL2ArcFormatting:
    """Tests for L2 short-term arc formatting."""

    def test_l2_arc_shows_summaries(self, sample_story_bible):
        """L2 formatting shows chapter summaries."""
        sample_story_bible.short_term_arc.append(
            ChapterSummary(chapter_number=1, summary="Hero wakes up")
        )
        result = _format_l2_arc(sample_story_bible)
        assert "Chapter 1" in result
        assert "Hero wakes up" in result

    def test_l2_arc_shows_multiple_summaries(self, sample_story_bible):
        """L2 formatting shows multiple summaries."""
        sample_story_bible.short_term_arc.append(
            ChapterSummary(chapter_number=1, summary="Hero wakes up")
        )
        sample_story_bible.short_term_arc.append(
            ChapterSummary(chapter_number=2, summary="Hero meets ally")
        )
        result = _format_l2_arc(sample_story_bible)
        assert "Chapter 1" in result
        assert "Chapter 2" in result
        assert "Hero wakes up" in result
        assert "Hero meets ally" in result

    def test_l2_arc_shows_fallback(self, sample_story_bible):
        """L2 formatting shows fallback when empty."""
        result = _format_l2_arc(sample_story_bible)
        assert "beginning" in result.lower()

    def test_l2_arc_limits_to_five(self, sample_story_bible):
        """L2 formatting limits output to last 5 summaries."""
        for i in range(1, 8):
            sample_story_bible.short_term_arc.append(
                ChapterSummary(chapter_number=i, summary=f"Chapter {i} summary")
            )
        result = _format_l2_arc(sample_story_bible)
        # Should show chapters 3-7 (last 5), not chapter 1 or 2
        assert "Chapter 3" in result
        assert "Chapter 7" in result
        assert "Chapter 1" not in result
        assert "Chapter 2" not in result


class TestL1RecentFormatting:
    """Tests for L1 recent chapters formatting."""

    def test_l1_recent_shows_chapters(self, sample_story_bible):
        """L1 formatting shows chapter content."""
        sample_story_bible.recent_chapters.append(
            Chapter(title="Ch1", content="Content here", chapter_number=1)
        )
        result = _format_l1_recent(sample_story_bible)
        assert "Chapter 1" in result
        assert "Content here" in result

    def test_l1_recent_shows_fallback(self, sample_story_bible):
        """L1 formatting shows fallback when empty."""
        result = _format_l1_recent(sample_story_bible)
        assert "No chapters" in result

    def test_l1_recent_limits_to_two(self, sample_story_bible):
        """L1 formatting limits output to last 2 chapters."""
        for i in range(1, 5):
            sample_story_bible.recent_chapters.append(
                Chapter(title=f"Ch{i}", content=f"Content {i}", chapter_number=i)
            )
        result = _format_l1_recent(sample_story_bible)
        # Should show chapters 3 and 4, not 1 or 2
        assert "Chapter 3" in result
        assert "Chapter 4" in result
        assert "Chapter 1" not in result
        assert "Chapter 2" not in result

    def test_l1_recent_truncates_long_content(self, sample_story_bible):
        """L1 formatting truncates chapter content to 1500 chars."""
        long_content = "x" * 2000
        sample_story_bible.recent_chapters.append(
            Chapter(title="Ch1", content=long_content, chapter_number=1)
        )
        result = _format_l1_recent(sample_story_bible)
        # Should contain truncated content (last 1500 chars)
        assert len(result) < 2000  # Much less than full 2000 chars


class TestL4CharactersFormatting:
    """Tests for L4 character registry formatting."""

    def test_l4_characters_shows_names(self, sample_story_bible):
        """L4 formatting shows character names."""
        sample_story_bible.characters.append(
            Character(
                name="Alice",
                description="Hero",
                character_type=CharacterType.PROTAGONIST,
            )
        )
        result = _format_l4_characters(sample_story_bible)
        assert "Alice" in result
        assert "Hero" in result

    def test_l4_characters_shows_personality(self, sample_story_bible):
        """L4 formatting includes personality when set."""
        sample_story_bible.characters.append(
            Character(
                name="Alice",
                description="Hero",
                character_type=CharacterType.PROTAGONIST,
                personality="Brave and kind",
            )
        )
        result = _format_l4_characters(sample_story_bible)
        assert "Brave and kind" in result

    def test_l4_characters_shows_fallback(self, sample_story_bible):
        """L4 formatting shows fallback when empty."""
        result = _format_l4_characters(sample_story_bible)
        assert "No characters" in result

    def test_l4_characters_shows_multiple(self, sample_story_bible):
        """L4 formatting shows multiple characters."""
        sample_story_bible.characters.append(
            Character(
                name="Alice",
                description="Hero",
                character_type=CharacterType.PROTAGONIST,
            )
        )
        sample_story_bible.characters.append(
            Character(
                name="Bob",
                description="Sidekick",
                character_type=CharacterType.SUPPORTING,
            )
        )
        result = _format_l4_characters(sample_story_bible)
        assert "Alice" in result
        assert "Bob" in result


class TestTemplateOrder:
    """Tests for template section ordering per D-06."""

    def test_template_has_correct_order(self):
        """Template sections appear in D-06 order: L3 -> L2 -> L1 -> L4."""
        # D-06: L3 -> L2 -> L1 -> L4
        l3_pos = STORY_CONTEXT_TEMPLATE.find("Story Overview")
        l2_pos = STORY_CONTEXT_TEMPLATE.find("Recent Developments")
        l1_pos = STORY_CONTEXT_TEMPLATE.find("Latest Chapters")
        l4_pos = STORY_CONTEXT_TEMPLATE.find("Active Characters")
        assert l3_pos < l2_pos < l1_pos < l4_pos

    def test_template_has_all_placeholders(self):
        """Template has all 4 tier placeholders."""
        assert "{story_overview}" in STORY_CONTEXT_TEMPLATE
        assert "{recent_developments}" in STORY_CONTEXT_TEMPLATE
        assert "{latest_chapters}" in STORY_CONTEXT_TEMPLATE
        assert "{active_characters}" in STORY_CONTEXT_TEMPLATE
