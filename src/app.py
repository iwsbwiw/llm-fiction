"""Streamlit main entry point for LLM Fiction.

Per D-01: Single-page application with session state management.
Two main states: 'input' (start page) and 'reading' (reading page).
"""

import streamlit as st


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
    except ImportError:
        pass  # sidebar.py not yet created

    # Route to page based on state (D-01)
    if st.session_state.app_state == "input":
        try:
            from src.ui.pages import render_input_page

            render_input_page()
        except ImportError:
            st.error("UI module not found. Please check installation.")
    elif st.session_state.app_state == "reading":
        try:
            from src.ui.pages import render_reading_page

            render_reading_page()
        except ImportError:
            st.error("Reading page not yet implemented.")


if __name__ == "__main__":
    main()
