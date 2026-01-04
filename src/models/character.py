"""Character model per D-07 specification."""
from enum import Enum

from pydantic import BaseModel, Field


class CharacterType(str, Enum):
    """Type of character in the story."""

    PROTAGONIST = "protagonist"
    SUPPORTING = "supporting"


class Character(BaseModel):
    """Character model per D-07 specification.

    Basic: name, description, character_type (protagonist/supporting)
    Background: personality, backstory, motivations
    Relationships: relationships[], development_arc
    """

    # Optional ID for storage layer
    id: str | None = None

    # Basic
    name: str
    description: str
    character_type: CharacterType

    # Background
    personality: str | None = None
    backstory: str | None = None
    motivations: str | None = None

    # Relationships
    relationships: list[str] = Field(default_factory=list)
    development_arc: str | None = None
