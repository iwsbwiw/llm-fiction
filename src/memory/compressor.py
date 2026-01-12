"""Chapter compression for memory management per D-11, D-12, D-13."""

from langchain_core.language_models import BaseChatModel

from src.memory.extractor import extract_chapter_info
from src.memory.models import ChapterSummary
from src.models import Chapter


COMPRESSION_PROMPT = """Summarize this chapter in 2-3 sentences for story continuity per D-12.

Chapter {chapter_number}:
{chapter_content}

Focus on: plot progression, character development, important revelations.

This summary will be used to maintain story coherence in future chapters."""


def compress_chapter(llm: BaseChatModel, chapter: Chapter) -> ChapterSummary:
    """Compress full chapter into L2 summary per D-11, D-12.

    Uses extract_chapter_info to get structured extraction, then
    builds ChapterSummary from the result.

    Args:
        llm: Language model for compression
        chapter: Chapter to compress

    Returns:
        ChapterSummary for L2 short-term arc
    """
    result = extract_chapter_info(llm, chapter)

    return ChapterSummary(
        chapter_number=chapter.chapter_number,
        summary=result.summary,
        key_plot_points=result.plot_developments
    )


def should_compress(story_bible) -> bool:
    """Check if L1 exceeds 2 chapters per D-11 threshold.

    Args:
        story_bible: Current StoryBible state

    Returns:
        True if compression should be triggered
    """
    return len(story_bible.recent_chapters) > 2
