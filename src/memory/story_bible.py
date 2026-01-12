"""StoryBibleManager with CRUD operations and tier limit enforcement."""

from src.memory.models import ChapterSummary, StoryBible
from src.models import Chapter, Character


class StoryBibleManager:
    """Manager for StoryBible CRUD operations with tier limit enforcement.

    Enforces memory tier limits per D-01 and D-02:
    - L1: max 2 recent chapters
    - L2: max 5 chapter summaries
    """

    def __init__(self, story_bible: StoryBible | None = None):
        """Initialize manager with optional existing StoryBible.

        Args:
            story_bible: Existing StoryBible to manage, or None to create new.
        """
        self.story_bible = story_bible or StoryBible()

    def add_chapter(self, chapter: Chapter) -> None:
        """Add chapter to L1, enforce max 2 limit per D-01.

        Args:
            chapter: Chapter to add to recent_chapters.
        """
        self.story_bible.recent_chapters.append(chapter)
        self._enforce_l1_limit()

    def add_summary(self, summary: ChapterSummary) -> None:
        """Add summary to L2, enforce max 5 limit per D-02.

        Args:
            summary: ChapterSummary to add to short_term_arc.
        """
        self.story_bible.short_term_arc.append(summary)
        self._enforce_l2_limit()

    def update_macro(self, macro: str) -> None:
        """Update L3 long-term macro per D-03.

        Args:
            macro: Single paragraph story overview.
        """
        self.story_bible.long_term_macro = macro

    def add_character(self, character: Character) -> None:
        """Add character to L4 entity registry per D-04.

        Args:
            character: Character to add to registry.
        """
        self.story_bible.characters.append(character)

    def _enforce_l1_limit(self) -> None:
        """Enforce L1 max 2 chapters per D-01."""
        if len(self.story_bible.recent_chapters) > 2:
            self.story_bible.recent_chapters = self.story_bible.recent_chapters[-2:]

    def _enforce_l2_limit(self) -> None:
        """Enforce L2 max 5 summaries per D-02."""
        if len(self.story_bible.short_term_arc) > 5:
            self.story_bible.short_term_arc = self.story_bible.short_term_arc[-5:]

    def get_context(self) -> StoryBible:
        """Return current story bible state.

        Returns:
            Current StoryBible instance.
        """
        return self.story_bible
