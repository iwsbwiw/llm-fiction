"""Agent schemas and nodes for multi-agent story generation."""

from src.agents.schemas import ChapterOutline, PacingIntent, ReviewResult, StoryInitialization
from src.agents.state import GenerationState

__all__ = [
    "ChapterOutline",
    "PacingIntent",
    "ReviewResult",
    "StoryInitialization",
    "GenerationState",
]

# Lazy imports to avoid config validation at module load time
def __getattr__(name: str):
    if name == "screenwriter_node":
        from src.agents.nodes import screenwriter_node

        return screenwriter_node
    if name == "writer_node":
        from src.agents.nodes import writer_node

        return writer_node
    if name == "reviewer_node":
        from src.agents.nodes import reviewer_node

        return reviewer_node
    if name == "initialize_story_node":
        from src.agents.nodes import initialize_story_node

        return initialize_story_node
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
