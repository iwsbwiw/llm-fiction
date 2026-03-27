"""Agent node implementations for LangGraph orchestration.

Per AGT-01, AGT-02, AGT-03:
- screenwriter_node: creates chapter outlines (temp 0.1)
- writer_node: produces narrative prose (temp 0.5)
- reviewer_node: checks quality and consistency (temp 0.2)

Per D-13, D-14:
- initialize_story_node: transforms one-liner into StoryBible (temp 0.3)
"""

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from src.agents.schemas import ChapterOutline, ReviewResult, StoryInitialization
from src.llm_client import create_llm_with_temp
from src.memory.context_injector import format_context
from src.memory.models import StoryBible
from src.models import Character, CharacterType


def _extract_json_object(text: str) -> str:
    """Extract the first JSON object from model output."""
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped

    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block_match:
        return code_block_match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1].strip()

    raise ValueError(f"Model did not return JSON. Raw output: {text[:300]}")


def _invoke_json_schema(llm, schema: type[BaseModel], messages: list) -> BaseModel:
    """Invoke model and parse a JSON response into the target schema."""
    schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False, indent=2)
    enforced_messages = [
        *messages,
        HumanMessage(
            content=(
                "Return only valid JSON that matches this schema exactly. "
                "Do not use markdown, headings, or explanation.\n\n"
                f"{schema_json}"
            )
        ),
    ]
    response = llm.invoke(enforced_messages)
    raw_content = response.content if hasattr(response, "content") else str(response)
    json_text = _extract_json_object(raw_content)
    return schema.model_validate_json(json_text)


def screenwriter_node(state: dict) -> dict:
    """Screenwriter agent: creates chapter outline per D-01, D-02.

    Per AGT-01: Temperature 0.1 (range 0.0-0.2)
    Per D-11: Receives L3 (macro) + L2 (arc summaries) + L4 (characters)
    Per D-02: Outline includes title, main_plot, character_appearances, pacing_intent, transition_note

    Args:
        state: LangGraph state containing story_bible, current_chapter, user_prompt.

    Returns:
        Dict with chapter_outline key containing JSON string of ChapterOutline.
    """
    llm = create_llm_with_temp(temperature=0.1)
    story_bible: StoryBible = state["story_bible"]
    current_chapter = state["current_chapter"]
    user_prompt = state.get("user_prompt", "")

    # Build context (L3 + L2 + L4 for outline planning per D-11)
    context = format_context(story_bible)

    is_first_chapter = current_chapter == 1 or not story_bible.recent_chapters

    transition_guidance = (
        "This is the first chapter — describe the opening atmosphere in transition_note."
        if is_first_chapter
        else f"""The previous chapter ended as follows. The new chapter MUST carry forward this scene, mood, or emotion naturally:

{context['transition_anchor']}"""
    )

    messages = [
        SystemMessage(content=f"""You are a screenwriter creating chapter outlines for a story.

Story Overview:
{context['story_overview']}

Recent Developments:
{context['recent_developments']}

Active Characters:
{context['active_characters']}

{transition_guidance}

Your task is to create an outline for Chapter {current_chapter}.
The outline should:
1. Have a compelling chapter title
2. Describe the main plot points for this chapter
3. List which characters will appear — PRIORITIZE existing characters from the Active Characters list above. Only introduce a new character if there is a strong narrative reason (e.g., a villain's debut, a key ally). Do NOT add new characters just for variety.
4. Set a pacing_intent that fits the story rhythm:
   - "setup": Lay groundwork, foreshadow, build atmosphere. Not every chapter needs to advance the main plot.
   - "escalation": Advance the plot, raise tension.
   - "climax": Peak intensity — major revelation or confrontation.
   - "reflection": Slow down — emotional processing, character bonding, daily life, aftermath of events.
5. Fill transition_note explaining how this chapter connects to the previous chapter's ending.
6. Only fill key_development when this chapter has a meaningful plot event. For "setup" and "reflection" chapters, leave key_development as null.

IMPORTANT pacing guidance:
- Do NOT make every chapter an escalation or climax. A healthy story alternates between fast and slow chapters.
- After a tense chapter, prefer "reflection" or "setup" to let readers breathe.
- Every 3-4 chapters, include at least one "reflection" chapter focused on character relationships and emotional depth.
- "climax" chapters should be rare (roughly every 5-8 chapters).

Follow the established story direction and character arcs."""),
        HumanMessage(content=user_prompt if user_prompt else f"Create the outline for Chapter {current_chapter}.")
    ]

    outline: ChapterOutline = _invoke_json_schema(llm, ChapterOutline, messages)

    return {
        "chapter_outline": outline.model_dump_json()
    }


def writer_node(state: dict) -> dict:
    """Writer agent: produces narrative prose per D-03.

    Per AGT-02: Temperature 0.5 (range 0.4-0.7)
    Per D-11: Receives all 4 tiers (full context for consistent prose)
    Per D-06: Handles revision feedback from reviewer

    Args:
        state: LangGraph state containing story_bible, chapter_outline, review_issues.

    Returns:
        Dict with chapter_content, and optionally revision_count increment.
    """
    llm = create_llm_with_temp(temperature=0.5)

    story_bible: StoryBible = state["story_bible"]
    chapter_outline = state.get("chapter_outline", "")
    review_issues = state.get("review_issues", [])

    # Build full context (all 4 tiers per D-11)
    context = format_context(story_bible)

    # Parse pacing_intent from outline for style guidance
    pacing_guidance = ""
    try:
        import json as _json
        outline_dict = _json.loads(chapter_outline) if isinstance(chapter_outline, str) else chapter_outline
        pacing = outline_dict.get("pacing_intent", "escalation")
        pacing_guidance = _pacing_style_instruction(pacing)
    except Exception:
        pass

    # Include revision feedback if this is a revision (D-06)
    revision_feedback = ""
    if review_issues:
        revision_feedback = f"""
Previous version had these issues to address:
{chr(10).join(f'- {issue}' for issue in review_issues)}

Please revise the chapter to address these issues while maintaining the story's flow and style.
"""

    messages = [
        SystemMessage(content=f"""You are a fiction writer. Write engaging narrative prose.

Story Context:
{context['story_overview']}

Recent Chapters:
{context['latest_chapters']}

Previous Chapter Ending (transition anchor):
{context['transition_anchor']}

Active Characters:
{context['active_characters']}

Chapter Outline:
{chapter_outline}

{pacing_guidance}

{revision_feedback}

TRANSITION REQUIREMENT: The opening of this chapter must naturally flow from the previous chapter's ending. Echo the closing scene, mood, or emotion before introducing new elements. Do NOT start as if the previous chapter never happened.

CHARACTER CONSTRAINT: Write about the characters listed in the outline. Do NOT introduce new named characters who are not in the Active Characters list above. Focus on deepening interactions between existing characters.

Write the chapter content. Be creative but stay true to the outline and character personalities."""),
        HumanMessage(content="Write approximately 2000 words of engaging prose for this chapter."),
    ]

    content = llm.invoke(messages).content

    updates = {"chapter_content": content}

    # Increment revision count if this is a revision (has issues from previous review)
    if review_issues:
        updates["revision_count"] = state.get("revision_count", 0) + 1
        updates["review_issues"] = []  # Clear for next iteration

    return updates


def _pacing_style_instruction(pacing: str) -> str:
    """Return style guidance based on the chapter's pacing intent."""
    instructions = {
        "setup": (
            "PACING: SETUP — Take your time establishing scenes and atmosphere. "
            "Use rich descriptions, foreshadowing, and measured dialogue. "
            "Allow readers to settle into the world before events unfold."
        ),
        "escalation": (
            "PACING: ESCALATION — Build momentum gradually. "
            "Each scene should raise the stakes a little higher. "
            "Balance action with moments of tension."
        ),
        "climax": (
            "PACING: CLIMAX — Write with intensity. "
            "Use shorter sentences and rapid scene changes. "
            "Dialogue should be sharp and urgent. "
            "Minimize lengthy descriptions — keep the reader on edge."
        ),
        "reflection": (
            "PACING: REFLECTION — Slow the narrative significantly. "
            "Focus on inner monologue, emotional processing, and quiet character moments. "
            "Include daily-life details, sensory descriptions, and unhurried dialogue. "
            "Let characters breathe and react to recent events. "
            "This is NOT a chapter for major plot advancement."
        ),
    }
    return instructions.get(pacing, "")


def reviewer_node(state: dict) -> dict:
    """Reviewer agent: checks quality per D-05.

    Per AGT-03: Temperature 0.2 (range 0.1-0.3)
    Per D-11: Receives L3 (macro) + L4 (characters) for consistency check
    Per D-05: Returns pass/fail + issues list

    Args:
        state: LangGraph state containing story_bible, chapter_content.

    Returns:
        Dict with review_passed (bool) and review_issues (list[str]).
    """
    llm = create_llm_with_temp(temperature=0.2)
    story_bible: StoryBible = state["story_bible"]
    chapter_content = state.get("chapter_content", "")
    chapter_outline = state.get("chapter_outline", "")

    # Build context (L3 + L4 for consistency check per D-11)
    context = format_context(story_bible)

    # Parse outline for pacing intent
    pacing_info = ""
    try:
        import json as _json
        outline_dict = _json.loads(chapter_outline) if isinstance(chapter_outline, str) else chapter_outline
        pacing = outline_dict.get("pacing_intent", "")
        if pacing:
            pacing_info = f"\nChapter pacing intent: {pacing}"
    except Exception:
        pass

    messages = [
        SystemMessage(content=f"""You are a story editor reviewing chapters for quality and consistency.

Story Context:
{context['story_overview']}

Active Characters:
{context['active_characters']}

Previous Chapter Ending:
{context['transition_anchor']}
{pacing_info}

Check for:
1. Character consistency (names, personalities, relationships)
2. Plot coherence (follows established timeline and logic)
3. Writing quality (pacing, dialogue, description)
4. TRANSITION QUALITY: Does the chapter opening naturally flow from the previous chapter's ending? The beginning should echo or carry forward the mood, scene, or emotion of the prior chapter's close. Mark as fail if the chapter starts as if the previous one never happened.
5. CHARACTER BLOAT: Are the named characters in this chapter mostly from the Active Characters list above? Flag as an issue if the chapter introduces multiple new named characters who don't appear in the list. One new character is acceptable; more than one usually indicates character bloat.
6. PACING MATCH: Does the writing style match the chapter's pacing intent? For "reflection" chapters, verify the prose is indeed slower with inner monologue and character moments. For "climax" chapters, verify the intensity is appropriate.

Return pass if the chapter is acceptable, or fail with specific issues that need to be addressed."""),
        HumanMessage(content=f"""Review this chapter:

{chapter_content}""")
    ]

    result: ReviewResult = _invoke_json_schema(llm, ReviewResult, messages)

    return {
        "review_passed": result.verdict == "pass",
        "review_issues": result.issues
    }


def initialize_story_node(state: dict) -> dict:
    """Initialize story from user one-liner prompt per D-13, D-14.

    Per D-14: Transforms user one-liner into initialized StoryBible.
    Temperature: 0.3 (balanced creativity for story setup)

    Args:
        state: LangGraph state containing user_prompt.

    Returns:
        Dict with story_bible key containing initialized StoryBible.
    """
    llm = create_llm_with_temp(temperature=0.3)
    user_prompt = state.get("user_prompt", "")

    messages = [
        SystemMessage(content="""You are a creative story architect. Your task is to transform a brief story idea into a complete story setup.

From the user's one-liner prompt, create:
1. A compelling title
2. The genre (e.g., fantasy, sci-fi, mystery, romance, thriller)
3. 2-4 main character names with brief descriptions
4. A story arc summary (2-3 sentences describing the overall narrative)
5. 3-5 initial chapter outlines that set up the story

Each chapter outline should have:
- A title
- Main plot points
- Character appearances
- A key turning point

Be creative but coherent. The story should have a clear beginning, middle, and planned direction."""),
        HumanMessage(content=f"Create a story from this idea: {user_prompt}")
    ]

    result: StoryInitialization = _invoke_json_schema(llm, StoryInitialization, messages)

    # Create StoryBible from the initialization result
    characters = []
    for i, char_name in enumerate(result.main_characters):
        char_type = CharacterType.PROTAGONIST if i == 0 else CharacterType.SUPPORTING
        characters.append(Character(
            name=char_name,
            description="To be developed",
            character_type=char_type
        ))

    story_bible = StoryBible(
        long_term_macro=result.story_arc,
        characters=characters,
        recent_chapters=[],
        short_term_arc=[]
    )

    return {"story_bible": story_bible}
