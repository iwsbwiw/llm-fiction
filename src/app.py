"""Streamlit main entry point for LLM Fiction.

Per D-01: Single-page application with session state management.
Two main states: 'input' (start page) and 'reading' (reading page).
"""

import sys
from pathlib import Path

import streamlit as st

# Ensure the project root is importable when launched via `streamlit run src/app.py`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    """Main entry point for the LLM Fiction application.

    Implements D-01 single-page state machine pattern.
    """
    # Page configuration (must be first Streamlit call)
    st.set_page_config(
        page_title="LLM Fiction",
        page_icon=":book:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Apply global styles
    try:
        from src.ui.styles import apply_global_styles

        apply_global_styles()
    except ImportError:
        pass  # styles.py not yet created

    # Initialize session state (D-01)
    if "app_state" not in st.session_state:
        st.session_state.app_state = "input"
    if "current_story_id" not in st.session_state:
        st.session_state.current_story_id = None
    if "current_chapter" not in st.session_state:
        st.session_state.current_chapter = 1
    if "user_prompt" not in st.session_state:
        st.session_state.user_prompt = ""

    # Render sidebar (D-03, D-04)
    try:
        from src.ui.sidebar import render_sidebar

        render_sidebar()
    except Exception as e:
        st.error(f"Sidebar failed to load: {e}")
        st.exception(e)

    # Route to page based on state (D-01)
    if st.session_state.app_state == "input":
        try:
            from src.ui.pages import render_input_page

            render_input_page()
        except Exception as e:
            st.error(f"Input page failed to load: {e}")
            st.exception(e)
    elif st.session_state.app_state == "reading":
        try:
            from src.ui.pages import render_reading_page

            render_reading_page()
        except Exception as e:
            st.error(f"Reading page failed to load: {e}")
            st.exception(e)


if __name__ == "__main__":
    main()
