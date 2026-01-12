"""StoryBible memory models with 4-tier architecture per D-01 to D-04."""

from pydantic import BaseModel, Field

from src.models import Chapter, Character


class ChapterSummary(BaseModel):
    """L2 short-term arc entry per D-02.

    A condensed summary of a chapter for the short-term memory tier.
    """

    chapter_number: int
    summary: str = Field(description="2-3 sentence summary")
    key_plot_points: list[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    """Structured output for chapter information extraction per D-09."""

    plot_developments: list[str] = Field(
        default_factory=list,
        description="Key plot points or events from this chapter"
    )
    character_updates: dict[str, str] = Field(
        default_factory=dict,
        description="Character name -> new information or development"
    )
    world_building_updates: str | None = Field(
        default=None,
        description="New world-building elements introduced"
    )
    summary: str = Field(
        description="2-3 sentence summary of this chapter per D-12"
    )


class StoryBible(BaseModel):
    """Root container for all story memory tiers per D-01 to D-04.

    L1 (Immediate): recent_chapters - max 2 full chapters
    L2 (Short-term): short_term_arc - max 5 chapter summaries
    L3 (Long-term): long_term_macro - single paragraph overview
    L4 (Entity): characters - entity registry using existing Character model
    """

    # L1: Immediate context - last 2 full chapters per D-01
    recent_chapters: list[Chapter] = Field(default_factory=list)

    # L2: Short-term arc - last 5 chapter summaries per D-02
    short_term_arc: list[ChapterSummary] = Field(default_factory=list)

    # L3: Long-term macro - single paragraph story overview per D-03
    long_term_macro: str | None = None

    # L4: Entity registry - characters per D-04 (reuses Character model)
    characters: list[Character] = Field(default_factory=list)
