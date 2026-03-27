"""Pydantic schemas for agent structured outputs.

Per D-02, D-05, D-14:
- ChapterOutline: Screenwriter's chapter plan
- ReviewResult: Reviewer's pass/fail verdict
- StoryInitialization: Initial story setup from user prompt
"""

from enum import Enum

from pydantic import BaseModel, Field
from typing import Literal, Optional


class PacingIntent(str, Enum):
    """Pacing intent for a chapter outline.

    - setup: Lay groundwork, foreshadow, build atmosphere
    - escalation: Advance the plot, raise tension
    - climax: Peak intensity, major revelation or confrontation
    - reflection: Slow down, emotional processing, character bonding, daily life
    """

    setup = "setup"
    escalation = "escalation"
    climax = "climax"
    reflection = "reflection"


class ChapterOutline(BaseModel):
    """Structured output for Screenwriter per D-02.

    Per D-02, outline includes: chapter title, main plot, character appearances,
    optional key development, transition note, and pacing intent.
    """

    title: str = Field(description="Chapter title")
    main_plot: str = Field(description="Main plot points for this chapter")
    character_appearances: list[str] = Field(
        default_factory=list,
        description="Characters appearing in this chapter. Prefer existing characters; only add new ones with strong justification."
    )
    key_development: Optional[str] = Field(
        default=None,
        description="Optional key plot development for this chapter. Omit for slow-paced chapters focused on character interaction or atmosphere."
    )
    transition_note: str = Field(
        description="How this chapter connects to the previous chapter's ending (scene, emotion, or narrative thread to carry forward). For chapter 1, describe the opening atmosphere."
    )
    pacing_intent: PacingIntent = Field(
        description="Pacing intent for this chapter: setup (lay groundwork), escalation (advance plot), climax (peak intensity), or reflection (slow down, emotional depth)."
    )


class ReviewResult(BaseModel):
    """Structured output for Reviewer per D-05.

    Per D-05, Reviewer returns: pass/fail + issues list.
    """

    verdict: Literal["pass", "fail"] = Field(
        description="Review verdict: pass or fail"
    )
    issues: list[str] = Field(
        default_factory=list,
        description="Issues to address if verdict is fail"
    )


class StoryInitialization(BaseModel):
    """Structured output for story initialization per D-14.

    Per D-14, transforms user one-liner into StoryBible-ready structure.
    """

    title: str = Field(description="Story title")
    genre: str = Field(description="Story genre (e.g., fantasy, sci-fi, mystery)")
    main_characters: list[str] = Field(
        default_factory=list,
        description="Names of main characters"
    )
    story_arc: str = Field(description="Overall story arc summary")
    initial_outline: list[ChapterOutline] = Field(
        default_factory=list,
        description="Initial chapter outlines for the story"
    )
