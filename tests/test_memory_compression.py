"""Tests for memory compression per D-11, D-12, D-13."""

import pytest

from src.memory import StoryBible, ChapterSummary
from src.memory.compressor import compress_chapter, should_compress, COMPRESSION_PROMPT
from src.models import Chapter


class TestCompression:
    def test_compress_chapter_returns_summary(self, mock_llm, sample_chapter):
        """Test compress_chapter returns ChapterSummary."""
        result = compress_chapter(mock_llm, sample_chapter)
        assert isinstance(result, ChapterSummary)
        assert result.chapter_number == sample_chapter.chapter_number

    def test_compress_chapter_has_summary_content(self, mock_llm, sample_chapter):
        """Test compress_chapter returns summary with content."""
        result = compress_chapter(mock_llm, sample_chapter)
        assert len(result.summary) > 0

    def test_should_compress_true_when_over_limit(self, sample_story_bible):
        """Test should_compress returns True when L1 > 2 per D-11."""
        # Add 3 chapters to exceed D-11 threshold of 2
        for i in range(3):
            sample_story_bible.recent_chapters.append(
                Chapter(title=f"Ch{i}", content="Content", chapter_number=i)
            )
        assert should_compress(sample_story_bible) is True

    def test_should_compress_false_when_at_limit(self, sample_story_bible):
        """Test should_compress returns False when L1 == 2."""
        # Add exactly 2 chapters (at limit)
        for i in range(2):
            sample_story_bible.recent_chapters.append(
                Chapter(title=f"Ch{i}", content="Content", chapter_number=i)
            )
        assert should_compress(sample_story_bible) is False

    def test_should_compress_false_when_under_limit(self, sample_story_bible):
        """Test should_compress returns False when L1 < 2."""
        # Add 1 chapter (under limit)
        sample_story_bible.recent_chapters.append(
            Chapter(title="Ch1", content="Content", chapter_number=1)
        )
        assert should_compress(sample_story_bible) is False

    def test_compression_prompt_mentions_2_3_sentences(self):
        """Test COMPRESSION_PROMPT mentions 2-3 sentences per D-12."""
        assert "2-3" in COMPRESSION_PROMPT or "two or three" in COMPRESSION_PROMPT.lower()
