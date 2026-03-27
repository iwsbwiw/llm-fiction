"""Sidebar navigation components per D-03, D-04."""
import streamlit as st

from src.storage.json_store import StoryStore


def render_chapter_navigation(store: StoryStore):
    """Render chapter navigation for current story.

    Args:
        store: StoryStore instance for loading story data.
    """
    current_story_id = st.session_state.get("current_story_id")
    current_chapter = st.session_state.get("current_chapter", 1)

    if not current_story_id:
        return

    try:
        data = store.load(current_story_id)
        chapters = data["chapters"]
        seen_chapter_nums: set[int] = set()

        st.markdown("### 章节")

        for chapter in chapters:
            chapter_num = chapter.chapter_number
            if chapter_num in seen_chapter_nums:
                continue
            seen_chapter_nums.add(chapter_num)
            is_current = chapter_num == current_chapter

            # Highlight current chapter with ▶ prefix (D-03)
            label = f"{'▶ ' if is_current else ''}第 {chapter_num} 章"

            if st.button(label, key=f"chapter_{chapter_num}", use_container_width=True):
                st.session_state.current_chapter = chapter_num
                st.rerun()
    except FileNotFoundError:
        st.caption("无法加载章节")


def render_sidebar():
    """Render sidebar with story archive and chapter navigation per D-03, D-04."""
    store = StoryStore()

    with st.sidebar:
        # Story archive section (D-04)
        st.markdown("### 我的小说")
        stories = store.list_stories()

        if not stories:
            st.caption("暂无存档")
        else:
            for story in stories:
                # Truncate long titles
                title = story["title"]
                label = title[:20] + ("..." if len(title) > 20 else "")

                if st.button(label, key=f"story_{story['id']}", use_container_width=True):
                    st.session_state.current_story_id = story["id"]
                    st.session_state.app_state = "reading"
                    st.session_state.current_chapter = 1
                    st.rerun()

        st.divider()

        # Chapter navigation (D-03) - only show when reading
        if st.session_state.get("app_state") == "reading" and st.session_state.get("current_story_id"):
            render_chapter_navigation(store)
