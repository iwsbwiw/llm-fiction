"""Chapter model per D-06 specification."""
from datetime import datetime

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    """Chapter model per D-06 specification.

    Basic: title, content, chapter_number, generated_at
    Outline: chapter_outline, plot_points, character_appearances
    Reading state: is_read, read_at
    """

    # Optional ID for storage layer
    id: str | None = None

    # Basic
    title: str
    content: str
    chapter_number: int
    generated_at: datetime = Field(default_factory=datetime.now)

    # Outline
    chapter_outline: str | None = None
    plot_points: list[str] = Field(default_factory=list)
    character_appearances: list[str] = Field(default_factory=list)

    # Reading state
    is_read: bool = False
    read_at: datetime | None = None
