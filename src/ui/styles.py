"""CSS utilities for LLM Fiction Streamlit app.

Per D-06: Default typography with 18px font and comfortable line-height.
"""
import streamlit as st


READING_CSS = """
<style>
.chapter-content {
    font-size: 18px;
    line-height: 1.8;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}
.chapter-content p {
    margin-bottom: 1.2em;
}
</style>
"""


def apply_global_styles() -> None:
    """Inject global CSS styles into the Streamlit app.

    Should be called once at app startup in main().
    """
    st.markdown(READING_CSS, unsafe_allow_html=True)


def render_chapter_content(content: str) -> None:
    """Render chapter content with proper typography.

    Args:
        content: The chapter text to render.
    """
    st.markdown(
        f'<div class="chapter-content">{content}</div>',
        unsafe_allow_html=True,
    )
