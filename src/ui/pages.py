"""Page render functions for LLM Fiction.

Implements D-01 single-page application with two main views:
- render_input_page: Google-style centered input for story creation (D-02)
- render_reading_page: Chapter reading interface per UI-03, D-06
"""

import streamlit as st

from src.storage.json_store import StoryStore
from src.ui.styles import render_chapter_content


def generate_next_chapter(story_id: str, story_bible, existing_chapters: list) -> "Chapter":
    """Generate next chapter and append to story.

    Args:
        story_id: Current story ID
        story_bible: Existing StoryBible state
        existing_chapters: List of existing Chapter objects

    Returns:
        The newly generated Chapter object.
    """
    from src.agents.graph import run_generation
    from src.models import Chapter

    next_chapter_num = len(existing_chapters) + 1

    # Generate next chapter
    initial_state = {
        "user_prompt": "",  # Not needed for continuation
        "story_bible": story_bible,
        "current_chapter": next_chapter_num,
        "revision_count": 0,
        "max_revisions": 3,
        "chapter_outline": None,
        "chapter_content": None,
        "review_passed": False,
        "review_issues": [],
        "completed_chapter": None,
    }

    result = run_generation(initial_state)
    new_chapter = result["completed_chapter"]

    # Load existing data and append
    store = StoryStore()
    data = store.load(story_id)

    data["chapters"].append(new_chapter)

    # Save updated story
    store.save(
        data["novel"],
        data["chapters"],
        data["characters"]
    )

    return new_chapter


def render_input_page():
    """Render the input page with centered Google-style layout.

    Implements D-02: Centered input layout like Google homepage.
    User enters one sentence to start a story.
    """
    # Top spacing for vertical centering
    st.markdown("")
    st.markdown("")
    st.markdown("")

    # 3-column layout: empty | content | empty (D-02)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Title with center alignment
        st.markdown(
            "<h3 style='text-align: center;'>输入一句话，开始你的故事</h3>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        # Text input with collapsed label for clean look
        user_input = st.text_input(
            label="story_prompt",
            placeholder="一个勇敢的骑士踏上了寻找失落的王国的旅程...",
            label_visibility="collapsed",
            key="story_prompt_input",
        )

        # Submit button
        if st.button("开始创作", use_container_width=True, key="start_story_btn"):
            if user_input and user_input.strip():
                from src.models import Novel, NovelStatus
                from src.memory import StoryBible
                from src.agents.graph import run_generation

                # Create novel
                novel = Novel(
                    title=user_input[:50] + ("..." if len(user_input) > 50 else ""),
                    one_sentence_prompt=user_input,
                    status=NovelStatus.IN_PROGRESS,
                )

                # Create initial story bible
                story_bible = StoryBible()
                story_bible.premise = user_input

                # Show generation status (text-only per D-05)
                status_placeholder = st.empty()
                status_placeholder.info("正在生成第 1 章...")

                try:
                    # Generate first chapter
                    initial_state = {
                        "user_prompt": user_input,
                        "story_bible": story_bible,
                        "current_chapter": 1,
                        "revision_count": 0,
                        "max_revisions": 3,
                        "chapter_outline": None,
                        "chapter_content": None,
                        "review_passed": False,
                        "review_issues": [],
                        "completed_chapter": None,
                    }

                    result = run_generation(initial_state)
                    chapter = result["completed_chapter"]

                    # Save to store
                    store = StoryStore()
                    story_id = store.save(novel, [chapter], [])

                    # Update session state
                    st.session_state.current_story_id = story_id
                    st.session_state.user_prompt = user_input
                    st.session_state.app_state = "reading"
                    st.session_state.current_chapter = 1

                    status_placeholder.empty()
                    st.rerun()

                except Exception as e:
                    status_placeholder.error(f"生成失败: {e}")


def render_reading_page():
    """Render reading page with chapter content per UI-03, D-06."""
    story_id = st.session_state.get("current_story_id")
    current_chapter = st.session_state.get("current_chapter", 1)

    if not story_id:
        st.markdown("### 请先选择一个故事")
        return

    try:
        store = StoryStore()
        data = store.load(story_id)
        chapters = data["chapters"]

        # Find current chapter
        chapter = next(
            (ch for ch in chapters if ch.chapter_number == current_chapter),
            chapters[0] if chapters else None
        )

        if not chapter:
            st.warning("暂无章节内容")
            return

        # Display chapter title
        st.markdown(f"## 第 {chapter.chapter_number} 章：{chapter.title}")

        st.divider()

        # Display chapter content with reading styles
        render_chapter_content(chapter.content)

        # Chapter navigation buttons per UI-04
        st.markdown("")
        st.markdown("")

        col_prev, col_next = st.columns(2)

        with col_prev:
            if current_chapter > 1:
                if st.button("← 上一章", key="prev_chapter_btn", use_container_width=True):
                    st.session_state.current_chapter = current_chapter - 1
                    st.rerun()
            else:
                st.button("← 上一章", key="prev_chapter_disabled", disabled=True, use_container_width=True)

        with col_next:
            if chapter and current_chapter < len(chapters):
                if st.button("下一章 →", key="next_chapter_btn", use_container_width=True):
                    st.session_state.current_chapter = current_chapter + 1
                    st.rerun()
            else:
                st.button("下一章 →", key="next_chapter_disabled", disabled=True, use_container_width=True)

        # Generate next chapter button
        st.markdown("")
        st.divider()
        st.markdown("")

        if st.button("生成下一章", key="generate_next_btn", use_container_width=True):
            status_placeholder = st.empty()
            next_num = len(chapters) + 1
            status_placeholder.info(f"正在生成第 {next_num} 章...")

            try:
                new_chapter = generate_next_chapter(story_id, data.get("story_bible"), chapters)

                # Navigate to new chapter
                st.session_state.current_chapter = next_num
                status_placeholder.empty()
                st.rerun()

            except Exception as e:
                status_placeholder.error(f"生成失败: {e}")

    except FileNotFoundError:
        st.error("故事文件未找到")
    except Exception as e:
        st.error(f"加载故事时出错: {e}")
