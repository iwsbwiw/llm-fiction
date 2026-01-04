"""Novel model per D-05 specification."""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class NovelStatus(str, Enum):
    """Status of a novel in the generation pipeline."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Novel(BaseModel):
    """Novel model per D-05 specification.

    Basic: title, one_sentence_prompt, created_at, status
    Metadata: genre, style_tags, target_chapters
    Story Bible: outline, world_building, main_arc
    Reading progress: user_rating, is_favorite, last_read_chapter
    """

    # Optional ID for storage layer
    id: str | None = None

    # Basic
    title: str
    one_sentence_prompt: str
    created_at: datetime = Field(default_factory=datetime.now)
    status: NovelStatus = NovelStatus.DRAFT

    # Metadata
    genre: str | None = None
    style_tags: list[str] = Field(default_factory=list)
    target_chapters: int = 10

    # Story Bible
    outline: str | None = None
    world_building: str | None = None
    main_arc: str | None = None

    # Reading progress
    user_rating: int | None = Field(default=None, ge=1, le=5)
    is_favorite: bool = False
    last_read_chapter: int = 0
