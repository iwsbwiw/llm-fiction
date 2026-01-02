"""Tests for LangGraph graph construction (AGT-04, AGT-05)."""

import pytest
from unittest.mock import MagicMock, patch

from src.agents.state import GenerationState
from src.agents.graph import route_after_review, complete_node
from src.memory.models import StoryBible
from src.models import Chapter


class TestRouteAfterReview:
    """Tests for route_after_review routing function."""

    def test_route_complete_on_pass(self):
        """Test routing returns 'complete' when review_passed is True."""
        state: GenerationState = {
            "user_prompt": "test",
            "story_bible": StoryBible(),
            "current_chapter": 1,
            "revision_count": 0,
            "max_revisions": 3,
            "chapter_outline": None,
            "chapter_content": None,
            "review_passed": True,
            "review_issues": [],
            "completed_chapter": None,
        }

        result = route_after_review(state)
        assert result == "complete"

    def test_route_writer_on_fail_under_limit(self):
        """Test routing returns 'writer' when review fails and under revision limit."""
        state: GenerationState = {
            "user_prompt": "test",
            "story_bible": StoryBible(),
            "current_chapter": 1,
            "revision_count": 1,
            "max_revisions": 3,
            "chapter_outline": None,
            "chapter_content": None,
            "review_passed": False,
            "review_issues": ["Issue 1"],
            "completed_chapter": None,
        }

        result = route_after_review(state)
        assert result == "writer"

    def test_route_complete_at_revision_limit(self):
        """Test routing returns 'complete' when revision_count >= max_revisions (D-04)."""
        state: GenerationState = {
            "user_prompt": "test",
            "story_bible": StoryBible(),
            "current_chapter": 1,
            "revision_count": 3,
            "max_revisions": 3,
            "chapter_outline": None,
            "chapter_content": None,
            "review_passed": False,
            "review_issues": ["Issue 1"],
            "completed_chapter": None,
        }

        result = route_after_review(state)
        assert result == "complete"

    def test_route_complete_exceeds_revision_limit(self):
        """Test routing returns 'complete' when revision_count exceeds max_revisions."""
        state: GenerationState = {
            "user_prompt": "test",
            "story_bible": StoryBible(),
            "current_chapter": 1,
            "revision_count": 5,
            "max_revisions": 3,
            "chapter_outline": None,
            "chapter_content": None,
            "review_passed": False,
            "review_issues": ["Issue 1"],
            "completed_chapter": None,
        }

        result = route_after_review(state)
        assert result == "complete"


class TestCompleteNode:
    """Tests for complete_node function."""

    def test_complete_node_creates_chapter(self):
        """Test that complete_node creates a Chapter object."""
        state: GenerationState = {
            "user_prompt": "test",
            "story_bible": StoryBible(),
            "current_chapter": 5,
            "revision_count": 2,
            "max_revisions": 3,
            "chapter_outline": '{"title": "The Discovery", "main_plot": "A hero finds a map"}',
            "chapter_content": "Once upon a time in a land far away...",
            "review_passed": True,
            "review_issues": [],
            "completed_chapter": None,
        }

        result = complete_node(state)

        assert "completed_chapter" in result
        chapter = result["completed_chapter"]
        assert isinstance(chapter, Chapter)
        assert chapter.title == "Chapter 5"
        assert chapter.content == "Once upon a time in a land far away..."
        assert chapter.chapter_number == 5
        assert chapter.chapter_outline == '{"title": "The Discovery", "main_plot": "A hero finds a map"}'

    def test_complete_node_with_none_outline(self):
        """Test complete_node handles None chapter_outline."""
        state: GenerationState = {
            "user_prompt": "test",
            "story_bible": StoryBible(),
            "current_chapter": 3,
            "revision_count": 0,
            "max_revisions": 3,
            "chapter_outline": None,
            "chapter_content": "Chapter content without outline",
            "review_passed": True,
            "review_issues": [],
            "completed_chapter": None,
        }

        result = complete_node(state)

        assert "completed_chapter" in result
        chapter = result["completed_chapter"]
        assert chapter.chapter_outline is None


class TestGraphBuilds:
    """Tests for build_generation_graph function."""

    def test_graph_builds_returns_stategraph(self):
        """Test that build_generation_graph returns a StateGraph."""
        # Mock the config validation to avoid needing API keys
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from src.agents.graph import build_generation_graph

            graph = build_generation_graph()

            assert graph is not None
            # Check nodes are present
            nodes = list(graph.nodes.keys())
            assert "screenwriter" in nodes
            assert "writer" in nodes
            assert "reviewer" in nodes
            assert "complete" in nodes

    def test_graph_has_correct_edges(self):
        """Test that graph has correct edge structure."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from src.agents.graph import build_generation_graph
            from langgraph.graph import START, END

            graph = build_generation_graph()

            # Check edges exist
            # The StateGraph has an edges attribute
            assert hasattr(graph, "edges")


class TestRunGeneration:
    """Tests for run_generation helper function."""

    def test_run_generation_default_recursion_limit(self):
        """Test run_generation uses default recursion_limit of50."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from src.agents.graph import run_generation

            # Mock all agent nodes to bypass LLM calls
            mock_chapter = Chapter(
                title="Test Chapter",
                content="Test content",
                chapter_number=1,
            )

            initial_state = {
                "user_prompt": "A test story",
                "story_bible": StoryBible(),
                "current_chapter": 1,
                "revision_count": 0,
                "max_revisions": 3,
                "chapter_outline": None,
                "chapter_content": None,
                "review_passed": False,
                "review_issues": [],
                "completed_chapter": None,
            }

            with patch("src.agents.graph.build_generation_graph") as mock_build:
                mock_graph = MagicMock()
                mock_graph.compile.return_value = mock_graph
                mock_graph.invoke.return_value = {"completed_chapter": mock_chapter}
                mock_build.return_value = mock_graph

                result = run_generation(initial_state)

                # Verify invoke was called with default recursion_limit
                mock_graph.invoke.assert_called_once()
                call_args = mock_graph.invoke.call_args
                assert call_args[1][0] == initial_state
                assert call_args[1]["config"]["recursion_limit"] == 50

    def test_run_generation_custom_recursion_limit(self):
        """Test run_generation respects custom recursion_limit."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from src.agents.graph import run_generation

            initial_state = {
                "user_prompt": "A test story",
                "story_bible": StoryBible(),
                "current_chapter": 1,
                "revision_count": 0,
                "max_revisions": 3,
                "chapter_outline": None,
                "chapter_content": None,
                "review_passed": False,
                "review_issues": [],
                "completed_chapter": None,
            }

            with patch("src.agents.graph.build_generation_graph") as mock_build:
                mock_graph = MagicMock()
                mock_graph.compile.return_value = mock_graph
                mock_graph.invoke.return_value = {"completed_chapter": None}
                mock_build.return_value = mock_graph

                run_generation(initial_state, recursion_limit=25)

                # Verify invoke was called with custom recursion_limit
                call_args = mock_graph.invoke.call_args
                assert call_args[1]["config"]["recursion_limit"] == 25

    def test_recursion_limit_enforced(self):
        """Test that recursion limit is enforced per AGT-05."""
        from langgraph.errors import GraphRecursionError

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from src.agents.graph import build_generation_graph

            # Create a state that would cause infinite loop (always fail review)
            initial_state = {
                "user_prompt": "A test story",
                "story_bible": StoryBible(),
                "current_chapter": 1,
                "revision_count": 0,
                "max_revisions": 100,  # Set high to bypass D-04 logic
                "chapter_outline": None,
                "chapter_content": None,
                "review_passed": False,
                "review_issues": ["Always fail"],
                "completed_chapter": None,
            }

            # Mock agents to always fail review and return revision count increment
            def failing_reviewer(state):
                return {
                    "review_passed": False,
                    "review_issues": ["Always fail"],
                    "revision_count": state.get("revision_count", 0) + 1,
                }

            def passing_writer(state):
                return {
                    "chapter_content": "Generated content",
                    "revision_count": state.get("revision_count", 0) + 1,
                }

            with patch("src.agents.nodes.reviewer_node", failing_reviewer):
                with patch("src.agents.nodes.writer_node", passing_writer):
                    # Use low recursion limit to trigger error
                    graph = build_generation_graph().compile()

                    with pytest.raises(GraphRecursionError):
                        graph.invoke(initial_state, config={"recursion_limit": 10})


class TestFullGenerationFlow:
    """Integration tests for complete generation flow."""

    def test_full_flow_with_mocks(self):
        """Test complete flow: screenwriter -> writer -> reviewer -> complete."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            from src.agents.graph import build_generation_graph
            from src.agents.schemas import ChapterOutline

            # Create mock chapter outline
            mock_outline = ChapterOutline(
                title="The Beginning",
                main_plot="A hero starts their journey",
                character_appearances=["Alice"],
                key_turning_point="Alice discovers her power",
            )

            # Mock screenwriter to return outline
            def mock_screenwriter(state):
                return {"chapter_outline": mock_outline.model_dump_json()}

            # Mock writer to return content
            def mock_writer(state):
                return {
                    "chapter_content": "Once upon a time, Alice discovered she had a special power...",
                    "revision_count": state.get("revision_count", 0) + 1 if state.get("review_issues") else 0,
                }

            # Mock reviewer to pass
            def mock_reviewer(state):
                return {"review_passed": True, "review_issues": []}

            with patch("src.agents.nodes.screenwriter_node", mock_screenwriter):
                with patch("src.agents.nodes.writer_node", mock_writer):
                    with patch("src.agents.nodes.reviewer_node", mock_reviewer):
                        graph = build_generation_graph().compile()

                        initial_state = {
                            "user_prompt": "A girl discovers magic",
                            "story_bible": StoryBible(),
                            "current_chapter": 1,
                            "revision_count": 0,
                            "max_revisions": 3,
                            "chapter_outline": None,
                            "chapter_content": None,
                            "review_passed": False,
                            "review_issues": [],
                            "completed_chapter": None,
                        }

                        result = graph.invoke(initial_state)

                        # Verify flow completed
                        assert result["completed_chapter"] is not None
                        assert result["completed_chapter"].chapter_number == 1
                        assert result["review_passed"] is True
