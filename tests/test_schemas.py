"""Tests for agent schemas (AGT-01, AGT-02, AGT-03)."""

import pytest

from src.agents.schemas import ChapterOutline, ReviewResult, StoryInitialization


class TestChapterOutline:
    """Tests for ChapterOutline schema."""

    def test_instantiation_with_valid_data(self):
        """Test ChapterOutline can be created with all required fields."""
        outline = ChapterOutline(
            title="The Beginning",
            main_plot="Hero discovers a mysterious artifact",
            character_appearances=["Alice", "Bob"],
            key_turning_point="Alice finds the ancient map"
        )

        assert outline.title == "The Beginning"
        assert outline.main_plot == "Hero discovers a mysterious artifact"
        assert outline.character_appearances == ["Alice", "Bob"]
        assert outline.key_turning_point == "Alice finds the ancient map"

    def test_character_appearances_defaults_to_empty_list(self):
        """Test that character_appearances defaults to empty list."""
        outline = ChapterOutline(
            title="Empty Chapter",
            main_plot="Nothing happens",
            key_turning_point="Still nothing"
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
            key_turning_point="Hero appears"
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
