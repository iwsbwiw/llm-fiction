"""LangGraph state definition for multi-agent story generation.

Per D-08, D-09:
- StoryBible as LangGraph state - agents read/write StoryBible fields directly
- State includes: current chapter number, revision count, latest generated chapter, review result
"""

from typing import TypedDict

from src.memory.models import StoryBible
from src.models import Chapter


class GenerationState(TypedDict):
    """LangGraph state for multi-agent story generation.

    Per D-08: StoryBible fields accessible to all agents.
    Per D-09: State tracks generation progress and agent outputs.
    """

    # Core inputs
    user_prompt: str  # Original one-liner from user

    # StoryBible reference (D-08: agents read/write directly)
    story_bible: StoryBible

    # Generation progress (D-09)
    current_chapter: int  # Chapter being generated
    revision_count: int  # Current chapter's revision attempts (D-07)
    max_revisions: int  # Per D-04: 3

    # Agent outputs
    chapter_outline: str | None  # Screenwriter's chapter outline
    chapter_content: str | None  # Writer's prose output
    review_passed: bool  # Reviewer's verdict
    review_issues: list[str]  # Issues list from Reviewer (D-05)

    # Final output
    completed_chapter: Chapter | None  # Approved chapter ready for storage
