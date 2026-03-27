"""LangGraph StateGraph construction for multi-agent story generation.

Per AGT-04: Supervisor coordinates agents through LangGraph orchestration
Per AGT-05: Hard iteration limit prevents infinite loops

Exports:
- route_after_review: Routing function for revision loop
- complete_node: Finalizes chapter for storage
- build_generation_graph: Creates the StateGraph builder
- run_generation: Invokes graph with recursion limit
"""

import json
from typing import Literal

from langgraph.graph import StateGraph, START, END

from src.agents.state import GenerationState
from src.models import Chapter


def route_after_review(state: GenerationState) -> Literal["writer", "complete"]:
    """Routing function for revision loop per D-04, D-05, D-07.

    Per D-04: Max 3 revisions - after 3 attempts, accept current version
    Per D-05: Reviewer returns pass/fail
    Per D-07: Counter tracks current chapter's revision count

    Args:
        state: Current LangGraph state containing review_passed, revision_count, max_revisions.

    Returns:
        "complete" if review passed or revision limit reached, "writer" otherwise.
    """
    if state["review_passed"]:
        return "complete"
    if state["revision_count"] >= state["max_revisions"]:
        return "complete"  # Accept current version per D-04
    return "writer"  # Send back for revision


def complete_node(state: GenerationState) -> dict:
    """Finalize chapter and prepare for storage.

    This node runs after review passes OR revision limit reached.
    Per D-10: Each agent node returns updated state fields.

    Args:
        state: Current LangGraph state containing chapter_content, chapter_outline, current_chapter.

    Returns:
        Dict with completed_chapter containing the finalized Chapter object.
    """
    # Try to extract the title from the outline JSON
    chapter_title = f"Chapter {state['current_chapter']}"
    outline_raw = state.get("chapter_outline", "")
    if outline_raw:
        try:
            outline_data = json.loads(outline_raw)
            if outline_data.get("title"):
                chapter_title = outline_data["title"]
        except (json.JSONDecodeError, TypeError):
            pass

    chapter = Chapter(
        title=chapter_title,
        content=state["chapter_content"],
        chapter_number=state["current_chapter"],
        chapter_outline=state.get("chapter_outline"),
    )
    return {"completed_chapter": chapter}


def build_generation_graph() -> StateGraph:
    """Build the multi-agent generation graph per AGT-04.

    Per AGT-04: Supervisor coordinates Screenwriter -> Writer -> Reviewer
    through conditional edges for the graph uses:
        - START -> "screenwriter"
        - "screenwriter" -> "writer"
        - "writer" -> "reviewer"
        - Conditional from "reviewer" using route_after_review
        - "complete" -> END

    Returns:
        StateGraph builder (not compiled) for caller to compile and invoke.
    """
    # Lazy import to avoid config validation at module load time
    from src.agents.nodes import screenwriter_node, writer_node, reviewer_node

    builder = StateGraph(GenerationState)

    # Add nodes
    builder.add_node("screenwriter", screenwriter_node)
    builder.add_node("writer", writer_node)
    builder.add_node("reviewer", reviewer_node)
    builder.add_node("complete", complete_node)

    # Add edges
    builder.add_edge(START, "screenwriter")
    builder.add_edge("screenwriter", "writer")
    builder.add_edge("writer", "reviewer")
    builder.add_conditional_edges(
        "reviewer",
        route_after_review,
        {"writer": "writer", "complete": "complete"}
    )
    builder.add_edge("complete", END)

    return builder


def run_generation(initial_state: dict, recursion_limit: int = 50) -> dict:
    """Run the generation graph with recursion limit per AGT-05.

    Per AGT-05: Hard iteration limit prevents infinite loops.
    Default recursion_limit of 50 provides safety net beyond the D-04 max_revisions=3 logic.
    The D-04 logic (max 3 revisions) should trigger first; recursion_limit is backup.

    Args:
        initial_state: Initial state dict for GenerationState fields.
            Must include: user_prompt, story_bible, current_chapter, revision_count, max_revisions.
        recursion_limit: Maximum number of graph steps before GraphRecursionError.

    Returns:
        Final state dict with completed_chapter field.
    """
    graph = build_generation_graph().compile()
    result = graph.invoke(initial_state, config={"recursion_limit": recursion_limit})
    return result
