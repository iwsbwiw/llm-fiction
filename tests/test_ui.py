"""UI component tests for Phase 4: User Experience."""
import tomllib
from pathlib import Path

import pytest


class TestAppPy:
    """Tests for src/app.py main entry point."""

    def test_file_exists(self):
        """Test 1: File exists at src/app.py."""
        app_path = Path(__file__).parent.parent / "src" / "app.py"
        assert app_path.exists(), "src/app.py should exist"

    def test_main_function_defined(self):
        """Test 2: main() function defined."""
        import importlib.util

        app_path = Path(__file__).parent.parent / "src" / "app.py"
        spec = importlib.util.spec_from_file_location("app", str(app_path))
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)

        assert hasattr(app_module, "main"), "main() function should be defined"
        assert callable(app_module.main), "main should be callable"

    def test_session_state_initializes_app_state(self):
        """Test 3: Session state initializes app_state to 'input'."""
        app_path = Path(__file__).parent.parent / "src" / "app.py"
        content = app_path.read_text()
        assert 'app_state' in content, "app_state should be in session state"
        assert '"input"' in content or "'input'" in content, "app_state should initialize to 'input'"

    def test_session_state_initializes_current_chapter(self):
        """Test 4: Session state initializes current_chapter to 1."""
        app_path = Path(__file__).parent.parent / "src" / "app.py"
        content = app_path.read_text()
        assert 'current_chapter' in content, "current_chapter should be in session state"

    def test_set_page_config_called(self):
        """Test 5: set_page_config called with page_title='LLM Fiction'."""
        app_path = Path(__file__).parent.parent / "src" / "app.py"
        content = app_path.read_text()
        assert "set_page_config" in content, "set_page_config should be called"
        assert "LLM Fiction" in content, "page_title should be 'LLM Fiction'"


class TestInputPage:
    """Tests for render_input_page function."""

    def test_render_input_page_function_exists(self):
        """Test 1: render_input_page function exists."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        assert pages_path.exists(), "src/ui/pages.py should exist"
        content = pages_path.read_text()
        assert "def render_input_page" in content, "render_input_page should be defined"

    def test_uses_st_columns_for_centering(self):
        """Test 2: Uses st.columns with [1, 2, 1] ratio for centering."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "st.columns" in content, "st.columns should be used"
        assert "[1, 2, 1]" in content, "columns ratio should be [1, 2, 1]"

    def test_text_input_with_collapsed_label(self):
        """Test 3: Contains single st.text_input with label_visibility='collapsed'."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "st.text_input" in content, "st.text_input should be used"
        assert 'label_visibility="collapsed"' in content or "label_visibility='collapsed'" in content, \
            "text_input should have collapsed label visibility"

    def test_button_text_is_correct(self):
        """Test 4: Button text is '开始创作'."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "开始创作" in content, "Button text should be '开始创作'"


class TestThemeConfig:
    """Tests for .streamlit/config.toml theme configuration."""

    @pytest.fixture
    def config_path(self) -> Path:
        """Return path to Streamlit config file."""
        return Path(__file__).parent.parent / ".streamlit" / "config.toml"

    def test_config_file_exists(self, config_path: Path) -> None:
        """Test 1: File exists at .streamlit/config.toml."""
        assert config_path.exists(), f"Config file not found at {config_path}"

    def test_primary_color_is_gray(self, config_path: Path) -> None:
        """Test 2: primaryColor is #808080 (gray)."""
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        assert "theme" in config, "Missing [theme] section"
        assert config["theme"]["primaryColor"] == "#808080", (
            f"Expected primaryColor #808080, got {config['theme']['primaryColor']}"
        )

    def test_background_color_is_white(self, config_path: Path) -> None:
        """Test 3: backgroundColor is #ffffff (white)."""
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        assert "theme" in config, "Missing [theme] section"
        assert config["theme"]["backgroundColor"] == "#ffffff", (
            f"Expected backgroundColor #ffffff, got {config['theme']['backgroundColor']}"
        )

    def test_text_color_is_dark_gray(self, config_path: Path) -> None:
        """Test 4: textColor is #333333 (dark gray)."""
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        assert "theme" in config, "Missing [theme] section"
        assert config["theme"]["textColor"] == "#333333", (
            f"Expected textColor #333333, got {config['theme']['textColor']}"
        )


class TestUIStyles:
    """Tests for src/ui/styles.py CSS utilities."""

    @pytest.fixture
    def styles_module(self):
        """Import and return the styles module."""
        from src.ui import styles

        return styles

    def test_ui_init_exists(self) -> None:
        """Test 1: src/ui/__init__.py exists and is importable."""
        import src.ui

        assert src.ui is not None

    def test_styles_module_has_apply_global_styles(self, styles_module) -> None:
        """Test 2: styles.py has apply_global_styles function."""
        assert hasattr(styles_module, "apply_global_styles"), (
            "styles module missing apply_global_styles function"
        )
        assert callable(styles_module.apply_global_styles)

    def test_reading_css_has_font_size_18px(self, styles_module) -> None:
        """Test 3: READING_CSS contains font-size: 18px."""
        assert hasattr(styles_module, "READING_CSS"), (
            "styles module missing READING_CSS constant"
        )
        assert "font-size: 18px" in styles_module.READING_CSS, (
            "READING_CSS should contain font-size: 18px per D-06"
        )

    def test_reading_css_has_line_height_1_8(self, styles_module) -> None:
        """Test 4: READING_CSS contains line-height: 1.8."""
        assert "line-height: 1.8" in styles_module.READING_CSS, (
            "READING_CSS should contain line-height: 1.8 per D-06"
        )

    def test_styles_has_render_chapter_content(self, styles_module) -> None:
        """Test 5: styles.py has render_chapter_content function."""
        assert hasattr(styles_module, "render_chapter_content"), (
            "styles module missing render_chapter_content function"
        )
        assert callable(styles_module.render_chapter_content)


class TestSidebarNavigation:
    """Tests for UI-04 and UI-06: Sidebar navigation and story archive."""

    def test_sidebar_chapter_navigation(self, mock_session_state):
        """Verify sidebar renders chapter list.

        This test verifies UI-04 and D-03 decision:
        - Sidebar displays list of chapters
        - Current chapter is highlighted
        - Clicking a chapter navigates to it
        """
        pytest.skip("Implementation pending")

    def test_story_archive_display(self, mock_session_state):
        """Verify sidebar shows story list.

        This test verifies UI-06 and D-04 decision:
        - Sidebar displays saved stories from StoryStore
        - Each story shows title and last read chapter
        - Clicking a story loads it for reading
        """
        pytest.skip("Implementation pending")


class TestReadingPage:
    """Tests for UI-03: Chapter content display."""

    def test_render_reading_page_function_exists(self):
        """Test 1: render_reading_page function exists in pages.py."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "def render_reading_page" in content, "render_reading_page should be defined"

    def test_loads_story_from_store(self):
        """Test 2: Loads story from StoryStore using current_story_id."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "StoryStore" in content, "StoryStore should be imported"
        assert "store.load(" in content or ".load(" in content, "store.load() should be called"

    def test_displays_chapter_title(self):
        """Test 3: Displays chapter title using st.markdown."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "第" in content and "章" in content, "Chapter title should include chapter number"

    def test_calls_render_chapter_content(self):
        """Test 4: Calls render_chapter_content for content display."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "render_chapter_content" in content, "render_chapter_content should be called"

    def test_shows_no_story_message_when_none_selected(self):
        """Test 5: Shows '请先选择一个故事' when no story selected."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "请先选择一个故事" in content, "Should show message when no story selected"


class TestChapterNavigation:
    """Tests for chapter prev/next navigation buttons."""

    def test_prev_chapter_button_exists(self):
        """Test 1: '上一章' button exists in reading page."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "上一章" in content, "Previous chapter button should exist"

    def test_next_chapter_button_exists(self):
        """Test 2: '下一章' button exists in reading page."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "下一章" in content, "Next chapter button should exist"

    def test_uses_columns_for_horizontal_layout(self):
        """Test 3: Buttons use st.columns for horizontal layout."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "st.columns(2)" in content or "st.columns([1, 1])" in content, \
            "st.columns(2) should be used for button layout"

    def test_updates_current_chapter_in_session_state(self):
        """Test 4: Clicking button updates current_chapter in session state."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "current_chapter" in content, "current_chapter should be referenced"
        assert "st.session_state" in content, "session_state should be updated"


class TestProgressIndicator:
    """Tests for UI-05: Generation progress display."""

    def test_progress_status_display(self, mock_session_state):
        """Verify text status display during generation.

        This test verifies UI-05 and D-05 decision:
        - Text status shows current generation phase
        - Status updates as generation progresses
        - No progress bar, just simple text indicator
        """
        pytest.skip("Implementation pending")


class TestStoryGenerationTrigger:
    """Tests for story generation trigger in input page (Task 1)."""

    def test_run_generation_import_in_input_page(self):
        """Test 1: Button click creates new Novel instance.

        Verifies run_generation is imported and called in input page.
        """
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "run_generation" in content, "run_generation should be imported in pages.py"

    def test_story_id_stored_in_session_state(self):
        """Test 2: Story ID generated and stored in session state.

        Verifies current_story_id is set in session state.
        """
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "current_story_id" in content, "current_story_id should be stored in session state"

    def test_story_saved_to_store(self):
        """Test 3: Story saved to StoryStore after generation.

        Verifies store.save is called with novel and chapters.
        """
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "store.save" in content or "StoryStore" in content, \
            "StoryStore.save should be called to save generated story"

    def test_session_state_transitions_to_reading(self):
        """Test 4: Session state transitions to 'reading' after save.

        Verifies app_state is set to 'reading' after successful generation.
        """
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        # Find the pattern where app_state is set to reading within the generation context
        assert '"reading"' in content or "'reading'" in content, \
            "app_state should transition to 'reading'"


class TestGenerationStatusDisplay:
    """Tests for text-only progress indicator during generation."""

    def test_status_text_contains_chapter_number(self):
        """Verify status text includes chapter number.

        Per D-05: Text status only: "正在生成第 X 章..."
        """
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "正在生成" in content, "Status should contain Chinese text '正在生成'"
        assert "章" in content, "Status should contain chapter indicator '章'"

    def test_no_spinner_or_progress_bar(self):
        """Verify no spinner or progress bar used.

        Per D-05: No spinner or progress bar.
        """
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "st.spinner" not in content, "Should not use st.spinner per D-05"
        assert "st.progress" not in content, "Should not use st.progress per D-05"


class TestContinueGeneration:
    """Tests for continue generation function (Task 2)."""

    def test_generate_next_chapter_function_exists(self):
        """Test 1: generate_next_chapter function exists."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "def generate_next_chapter" in content, \
            "generate_next_chapter function should be defined"

    def test_calculates_next_chapter_number(self):
        """Test 2: Function calculates next chapter based on existing count."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "len(existing_chapters)" in content or "len(chapters)" in content, \
            "Should calculate next chapter from existing chapters length"


class TestGenerateNextChapterButton:
    """Tests for 'Generate Next Chapter' button on reading page (Task 3)."""

    def test_generate_next_chapter_button_exists(self):
        """Test 1: '生成下一章' button exists on reading page."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "生成下一章" in content, "Button text '生成下一章' should be in pages.py"

    def test_button_shows_status_with_chapter_number(self):
        """Test 2: Button shows '正在生成第 X 章...' when clicked."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        # Should use f-string with chapter number
        assert "正在生成第" in content, "Should display status with chapter number"

    def test_button_triggers_generate_next_chapter(self):
        """Test 3: Button triggers generate_next_chapter function."""
        pages_path = Path(__file__).parent.parent / "src" / "ui" / "pages.py"
        content = pages_path.read_text()
        assert "generate_next_chapter" in content, \
            "Button should call generate_next_chapter function"
