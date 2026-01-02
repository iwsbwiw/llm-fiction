"""Pydantic schemas for agent structured outputs.

Per D-02, D-05, D-14:
- ChapterOutline: Screenwriter's chapter plan
- ReviewResult: Reviewer's pass/fail verdict
- StoryInitialization: Initial story setup from user prompt
"""

from pydantic import BaseModel, Field
from typing import Literal


class ChapterOutline(BaseModel):
    """Structured output for Screenwriter per D-02.

    Per D-02, outline includes: chapter title, main plot, character appearances,
    key turning point.
    """

    title: str = Field(description="Chapter title")
    main_plot: str = Field(description="Main plot points for this chapter")
    character_appearances: list[str] = Field(
        default_factory=list,
        description="Characters appearing in this chapter"
    )
    key_turning_point: str = Field(
        description="Key plot twist or development in this chapter"
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
