"""LLM-based information extraction from chapters per D-09."""

from langchain_core.language_models import BaseChatModel

from src.memory.models import ExtractionResult
from src.models import Chapter


EXTRACTION_PROMPT = """Extract key information from this chapter for story continuity.

Chapter {chapter_number}:
{chapter_content}

Identify:
1. Plot developments (key events, revelations, turning points)
2. Character updates (new info about any character)
3. World-building elements (new locations, rules, lore)
4. A 2-3 sentence summary

Focus on information that should be remembered for future chapters."""


def create_extractor(llm: BaseChatModel):
    """Create structured extractor using with_structured_output per D-09.

    Args:
        llm: Language model instance (ChatOpenAI, ChatAnthropic, etc.)

    Returns:
        Structured LLM that returns ExtractionResult
    """
    return llm.with_structured_output(ExtractionResult)


def extract_chapter_info(llm: BaseChatModel, chapter: Chapter) -> ExtractionResult:
    """Extract structured information from a chapter per D-09.

    Args:
        llm: Language model for extraction
        chapter: Chapter to extract info from

    Returns:
        ExtractionResult with plot, character, world-building, and summary
    """
    extractor = create_extractor(llm)
    prompt = EXTRACTION_PROMPT.format(
        chapter_number=chapter.chapter_number,
        chapter_content=chapter.content
    )
    return extractor.invoke(prompt)
