"""JSON file storage for stories per D-08, D-09, D-10."""
import json
from datetime import datetime
from pathlib import Path

from src.config import settings
from src.memory.models import StoryBible
from src.models import Character, Chapter, Novel


class StoryStore:
    """JSON file storage per D-08, D-09, D-10.

    D-08: Single file per story — all data in one JSON file
    D-09: Flat directory structure: data/stories/{story-id}.json
    D-10: Story ID format: timestamp {YYYYMMDD-HHMMSS}
    """

    def __init__(self, base_dir: Path | str | None = None):
        """Initialize storage with base directory.

        Args:
            base_dir: Directory to store story JSON files.
        """
        self.base_dir = Path(base_dir or settings.data_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _generate_id(self) -> str:
        """Generate story ID per D-10: {YYYYMMDD-HHMMSS}.

        Returns:
            Story ID string in format YYYYMMDD-HHMMSS.
        """
        return datetime.now().strftime("%Y%m%d-%H%M%S")

    def save(
        self,
        novel: Novel,
        chapters: list[Chapter],
        characters: list[Character],
        story_bible: StoryBible | None = None,
    ) -> str:
        """Save story to JSON file.

        Args:
            novel: Novel metadata.
            chapters: List of chapters.
            characters: List of characters.
            story_bible: Current story bible state for future chapter generation.

        Returns:
            Story ID (used as filename).
        """
        story_id = novel.id or self._generate_id()
        filepath = self.base_dir / f"{story_id}.json"

        data = {
            "novel": novel.model_dump(),
            "chapters": [c.model_dump() for c in chapters],
            "characters": [c.model_dump() for c in characters],
            "story_bible": story_bible.model_dump() if story_bible else None,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        return story_id

    def load(self, story_id: str) -> dict:
        """Load story from JSON file.

        Args:
            story_id: Story ID (filename without .json extension).

        Returns:
            Dict with "novel", "chapters", "characters" keys containing
            reconstructed Pydantic models.
        """
        filepath = self.base_dir / f"{story_id}.json"

        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)

        return {
            "novel": Novel.model_validate(data["novel"]),
            "chapters": [Chapter.model_validate(c) for c in data["chapters"]],
            "characters": [Character.model_validate(c) for c in data["characters"]],
            "story_bible": (
                StoryBible.model_validate(data["story_bible"])
                if data.get("story_bible")
                else StoryBible()
            ),
        }

    def list_stories(self) -> list[dict]:
        """List all saved stories with metadata per UI-06.

        Returns:
            List of dicts with: id, title, last_read_chapter, chapter_count, created_at.
            Sorted by created_at descending (most recent first).
            Corrupted files are silently skipped.
        """
        stories = []
        for filepath in self.base_dir.glob("*.json"):
            try:
                data = self.load(filepath.stem)
                novel = data["novel"]
                stories.append({
                    "id": filepath.stem,
                    "title": novel.title,
                    "last_read_chapter": novel.last_read_chapter,
                    "chapter_count": len(data["chapters"]),
                    "created_at": novel.created_at.isoformat() if novel.created_at else None,
                })
            except Exception:
                continue  # Skip corrupted files

        # Sort by most recent first (created_at descending)
        stories.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return stories
