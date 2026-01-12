"""Tests for information extraction per D-09."""

import pytest

from src.memory import ExtractionResult, extract_chapter_info, create_extractor
from src.memory.models import ExtractionResult as ExtractionResultModel
from src.models import Chapter


class TestExtraction:
    def test_extraction_result_has_required_fields(self):
        """Test ExtractionResult model has all required fields."""
        result = ExtractionResult(
            summary="Test summary"
        )
        assert hasattr(result, "plot_developments")
        assert hasattr(result, "character_updates")
        assert hasattr(result, "world_building_updates")
        assert hasattr(result, "summary")

    def test_create_extractor_returns_callable(self, mock_llm):
        """Test create_extractor returns a callable with invoke method."""
        extractor = create_extractor(mock_llm)
        assert callable(extractor.invoke)

    def test_extract_chapter_info_returns_result(self, mock_llm, sample_chapter):
        """Test extract_chapter_info returns ExtractionResult."""
        result = extract_chapter_info(mock_llm, sample_chapter)
        assert isinstance(result, ExtractionResult)
        assert result.summary  # Has content

    def test_extraction_result_defaults(self):
        """Test ExtractionResult has sensible defaults."""
        result = ExtractionResult(summary="Test")
        assert result.plot_developments == []
        assert result.character_updates == {}
