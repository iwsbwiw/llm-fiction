"""Context injection system using fixed template per D-05, D-06.

Purpose: Inject Story Bible context into LLM prompts for consistent chapter generation.
"""

from langchain_core.prompts import ChatPromptTemplate

from src.memory.models import StoryBible


STORY_CONTEXT_TEMPLATE = """You are a creative fiction writer continuing a story.

## Story Overview
{story_overview}

## Recent Developments
{recent_developments}

## Latest Chapters
{latest_chapters}

## Active Characters
{active_characters}

---

Continue the story based on the above context. Write the next chapter."""


def format_context(story_bible: StoryBible) -> dict:
    """Format each tier for template injection per D-06 order: L3 -> L2 -> L1 -> L4.

    Args:
        story_bible: Current story state with all 4 tiers.

    Returns:
        Dict with formatted strings for each tier section, including transition anchor.
    """
    return {
        "story_overview": _format_l3_macro(story_bible),
        "recent_developments": _format_l2_arc(story_bible),
        "latest_chapters": _format_l1_recent(story_bible),
        "active_characters": _format_l4_characters(story_bible),
        "transition_anchor": _format_transition_anchor(story_bible),
    }


def inject_context(story_bible: StoryBible, generation_request: str) -> list:
    """Build complete message list for LLM invocation per D-05.

    Args:
        story_bible: Current story state with all 4 tiers.
        generation_request: User's request for next chapter.

    Returns:
        List of messages in LangChain format ready for invoke().
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", STORY_CONTEXT_TEMPLATE),
        ("human", "{generation_request}")
    ])

    context = format_context(story_bible)
    context["generation_request"] = generation_request

    return prompt.format_messages(**context)


def _format_l3_macro(story_bible: StoryBible) -> str:
    """Format L3 long-term macro per D-03.

    Returns the story overview or a fallback for new stories.
    """
    return story_bible.long_term_macro or "A new story begins."


def _format_l2_arc(story_bible: StoryBible) -> str:
    """Format L2 short-term arc summaries as bullet list per D-02.

    Shows up to the last 5 chapter summaries.
    """
    if not story_bible.short_term_arc:
        return "This is the beginning of the story."

    lines = []
    for summary in story_bible.short_term_arc[-5:]:
        lines.append(f"Chapter {summary.chapter_number}: {summary.summary}")
    return "\n".join(lines)


def _format_l1_recent(story_bible: StoryBible) -> str:
    """Format L1 recent chapters with content truncation per D-01.

    Shows up to the last 2 chapters, truncated to 1500 chars each to manage tokens.
    """
    if not story_bible.recent_chapters:
        return "No chapters written yet."

    parts = []
    for ch in story_bible.recent_chapters[-2:]:
        content = ch.content[-1500:] if len(ch.content) > 1500 else ch.content
        parts.append(f"[Chapter {ch.chapter_number}]\n{content}")
    return "\n\n---\n\n".join(parts)


def _format_transition_anchor(story_bible: StoryBible) -> str:
    """Extract the ending of the most recent chapter as a transition anchor.

    Returns the last 500 characters of the last chapter, so the next chapter
    can naturally carry forward the closing scene, mood, or emotion.
    """
    if not story_bible.recent_chapters:
        return "This is the first chapter — establish the opening atmosphere."

    last_ch = story_bible.recent_chapters[-1]
    tail = last_ch.content[-500:] if len(last_ch.content) > 500 else last_ch.content
    return f"[End of Chapter {last_ch.chapter_number} — last ~500 chars]\n{tail}"


def _format_l4_characters(story_bible: StoryBible) -> str:
    """Format L4 character registry per D-04.

    Lists all characters with their descriptions and personalities.
    """
    if not story_bible.characters:
        return "No characters established yet."

    lines = []
    for char in story_bible.characters:
        desc = f"{char.name}: {char.description}"
        if char.personality:
            desc += f" ({char.personality})"
        lines.append(f"- {desc}")
    return "\n".join(lines)
