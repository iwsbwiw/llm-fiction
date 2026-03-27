"""Tests for agent schemas (AGT-01, AGT-02, AGT-03)."""

import pytest

from src.agents.schemas import ChapterOutline, PacingIntent, ReviewResult, StoryInitialization


class TestChapterOutline:
    """Tests for ChapterOutline schema."""

    def test_instantiation_with_valid_data(self):
        """Test ChapterOutline can be created with all required fields."""
        outline = ChapterOutline(
            title="The Beginning",
            main_plot="Hero discovers a mysterious artifact",
            character_appearances=["Alice", "Bob"],
            key_development="Alice finds the ancient map",
            transition_note="Opens with Alice staring at the sunset from the hilltop",
            pacing_intent=PacingIntent.setup,
        )

        assert outline.title == "The Beginning"
        assert outline.main_plot == "Hero discovers a mysterious artifact"
        assert outline.character_appearances == ["Alice", "Bob"]
        assert outline.key_development == "Alice finds the ancient map"
        assert outline.pacing_intent == PacingIntent.setup

    def test_key_development_is_optional(self):
        """Test that key_development can be None for slow-paced chapters."""
        outline = ChapterOutline(
            title="A Quiet Day",
            main_plot="Characters rest and talk",
            transition_note="Continues from the calm after the storm",
            pacing_intent=PacingIntent.reflection,
        )

        assert outline.key_development is None

    def test_character_appearances_defaults_to_empty_list(self):
        """Test that character_appearances defaults to empty list."""
        outline = ChapterOutline(
            title="Empty Chapter",
            main_plot="Nothing happens",
            transition_note="Same scene continues",
            pacing_intent=PacingIntent.setup,
        )

        assert outline.character_appearances == []


class TestReviewResult:
    """Tests for ReviewResult schema."""

    def test_pass_verdict(self):
        """Test ReviewResult with pass verdict and no issues."""
        result = ReviewResult(verdict="pass", issues=[])

        assert result.verdict == "pass"
        assert result.issues == []

    def test_fail_verdict_with_issues(self):
        """Test ReviewResult with fail verdict and issue list."""
        result = ReviewResult(
            verdict="fail",
            issues=["Character inconsistency", "Pacing too slow"]
        )

        assert result.verdict == "fail"
        assert len(result.issues) == 2
        assert "Character inconsistency" in result.issues

    def test_issues_defaults_to_empty_list(self):
        """Test that issues defaults to empty list."""
        result = ReviewResult(verdict="pass")

        assert result.issues == []


class TestStoryInitialization:
    """Tests for StoryInitialization schema."""

    def test_instantiation_with_valid_data(self):
        """Test StoryInitialization can be created with all fields."""
        outline1 = ChapterOutline(
            title="Chapter 1",
            main_plot="Introduction",
            key_development="Hero appears",
            transition_note="Establish the world and tone",
            pacing_intent=PacingIntent.setup,
        )

        init = StoryInitialization(
            title="The Great Adventure",
            genre="fantasy",
            main_characters=["Alice", "Bob"],
            story_arc="A hero's journey to save the world",
            initial_outline=[outline1]
        )

        assert init.title == "The Great Adventure"
        assert init.genre == "fantasy"
        assert init.main_characters == ["Alice", "Bob"]
        assert init.story_arc == "A hero's journey to save the world"
        assert len(init.initial_outline) == 1

    def test_optional_fields_default_to_empty(self):
        """Test that list fields default to empty lists."""
        init = StoryInitialization(
            title="Minimal Story",
            genre="mystery",
            story_arc="Someone solves a crime"
        )

        assert init.main_characters == []
        assert init.initial_outline == []
