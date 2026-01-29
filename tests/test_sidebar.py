"""Tests for sidebar navigation components (UI-04, UI-06)."""
import re
from unittest.mock import MagicMock, patch
import pytest


class TestSidebarModule:
    """Tests for sidebar module structure and content."""

    def test_render_sidebar_function_exists(self):
        """Test 1: render_sidebar function exists."""
        from src.ui.sidebar import render_sidebar

        assert callable(render_sidebar)

    def test_render_sidebar_uses_st_sidebar(self):
        """Test 2: render_sidebar uses st.sidebar context manager."""
        # Read the source file and verify it uses st.sidebar
        import src.ui.sidebar as sidebar_module
        import inspect

        source = inspect.getsource(sidebar_module.render_sidebar)
        assert "with st.sidebar:" in source, "render_sidebar should use 'with st.sidebar:' context"

    def test_story_archive_section_header(self):
        """Test 3: Story archive section has '### 我的小说' header."""
        import src.ui.sidebar as sidebar_module
        import inspect

        source = inspect.getsource(sidebar_module)
        assert "### 我的小说" in source, "Sidebar should contain '### 我的小说' header"

    def test_chapter_navigation_section_header(self):
        """Test 4: Chapter navigation section has '### 章节' header."""
        import src.ui.sidebar as sidebar_module
        import inspect

        source = inspect.getsource(sidebar_module)
        assert "### 章节" in source, "Sidebar should contain '### 章节' header for chapter navigation"

    def test_current_chapter_highlight_prefix(self):
        """Test 5: Current chapter has '▶' prefix for highlighting."""
        import src.ui.sidebar as sidebar_module
        import inspect

        source = inspect.getsource(sidebar_module)
        assert "▶" in source, "Sidebar should use '▶' prefix to highlight current chapter"


class TestRenderChapterNavigation:
    """Tests for render_chapter_navigation helper function."""

    def test_render_chapter_navigation_exists(self):
        """Test that render_chapter_navigation helper function exists."""
        from src.ui.sidebar import render_chapter_navigation

        assert callable(render_chapter_navigation)

    def test_render_chapter_navigation_uses_story_store(self):
        """Test that render_chapter_navigation loads story from store."""
        import src.ui.sidebar as sidebar_module
        import inspect

        source = inspect.getsource(sidebar_module.render_chapter_navigation)
        assert "store.load" in source, "render_chapter_navigation should call store.load()"

    def test_render_chapter_navigation_updates_session_state(self):
        """Test that clicking chapter updates session state."""
        import src.ui.sidebar as sidebar_module
        import inspect

        source = inspect.getsource(sidebar_module.render_chapter_navigation)
        assert "st.session_state.current_chapter" in source, \
            "render_chapter_navigation should update st.session_state.current_chapter"
        assert "st.rerun()" in source, \
            "render_chapter_navigation should call st.rerun() after navigation"


class TestSidebarIntegration:
    """Integration tests for sidebar with StoryStore."""

    def test_sidebar_imports_story_store(self):
        """Test that sidebar module imports StoryStore."""
        import src.ui.sidebar as sidebar_module

        # Check that StoryStore is available in the module's namespace
        assert hasattr(sidebar_module, "StoryStore") or "StoryStore" in dir(sidebar_module)

    def test_render_sidebar_calls_list_stories(self):
        """Test that render_sidebar calls StoryStore.list_stories()."""
        import src.ui.sidebar as sidebar_module
        import inspect

        source = inspect.getsource(sidebar_module.render_sidebar)
        assert "list_stories" in source, "render_sidebar should call list_stories()"

    def test_story_button_updates_session_state(self):
        """Test that clicking story button updates session state."""
        import src.ui.sidebar as sidebar_module
        import inspect

        source = inspect.getsource(sidebar_module.render_sidebar)
        # Check that clicking a story updates relevant session state
        assert "st.session_state.current_story_id" in source, \
            "render_sidebar should update current_story_id"
        assert "st.session_state.app_state" in source, \
            "render_sidebar should update app_state"
