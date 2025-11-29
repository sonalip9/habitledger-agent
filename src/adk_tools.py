"""
ADK tool definitions for behaviour analysis.

This module contains tool definitions and factory functions for ADK integration,
extracted to avoid circular dependencies between coach and agent modules.
"""

import logging
import time
from pathlib import Path
from typing import Any

from google.genai.types import FunctionDeclaration, Schema, Tool, Type

from src.behaviour_engine import analyse_behaviour, load_behaviour_db
from src.memory import MAX_CONVERSATION_CONTEXT_LENGTH, UserMemory


logger = logging.getLogger(__name__)


def behaviour_db_tool(
    user_input: str, _session_meta: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Analyze user financial habit input and detect relevant behavioural principle.

    This function serves as an ADK FunctionTool that the agent can call at runtime
    to analyze user behaviour and get structured recommendations. It loads the
    behaviour principles database, runs classification (ADK or keyword-based),
    and returns structured intervention suggestions.

    Args:
        user_input: The user's description of their financial habit, struggle, or goal.
        session_meta: Optional session metadata containing user context (unused for now).

    Returns:
        dict: A structured response with:
            - "detected_principle_id" (str | None): ID of the matched principle
            - "interventions" (list[str]): List of suggested intervention strategies
            - "explanation" (str): Human-readable explanation of the detection

    Example:
        >>> result = behaviour_db_tool("I keep ordering food delivery every evening")
        >>> print(result["detected_principle_id"])
        friction_increase
    """
    start_time = time.time()

    try:
        # Load behaviour database
        db_path = Path(__file__).parent.parent / "data" / "behaviour_principles.json"
        behaviour_db = load_behaviour_db(str(db_path))

        # Create minimal memory for analysis
        memory = UserMemory(user_id="adk_tool_user")

        # Analyze behaviour
        analysis = analyse_behaviour(user_input, memory, behaviour_db)

        principle_id = analysis.get("detected_principle_id")
        interventions = analysis.get("intervention_suggestions", [])

        # Build explanation
        if principle_id:
            explanation = analysis.get(
                "reasoning", f"Detected principle: {principle_id}"
            )
        else:
            explanation = "Could not confidently detect a specific principle."

        # Log success
        duration_ms = int((time.time() - start_time) * 1000)
        source = analysis.get("source", "unknown")
        user_input_truncated = (
            user_input[:MAX_CONVERSATION_CONTEXT_LENGTH]
            if len(user_input) > MAX_CONVERSATION_CONTEXT_LENGTH
            else user_input
        )

        logger.info(
            "behaviour_db_tool executed successfully",
            extra={
                "event": "tool_call",
                "tool_name": "behaviour_db_tool",
                "principle_id": principle_id,
                "source": source,
                "user_input": user_input_truncated,
                "duration_ms": duration_ms,
            },
        )

        return {
            "detected_principle_id": principle_id,
            "interventions": interventions,
            "explanation": explanation,
        }
    except Exception as e:  # noqa: BLE001
        duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            "behaviour_db_tool failed: %s",
            str(e),
            extra={
                "event": "tool_call",
                "tool_name": "behaviour_db_tool",
                "error": str(e),
                "duration_ms": duration_ms,
            },
            exc_info=True,
        )
        return {
            "detected_principle_id": None,
            "interventions": [],
            "explanation": f"Error analyzing behaviour: {str(e)}",
        }


def create_behaviour_db_function_tool() -> Tool:
    """
    Create the behaviour DB analysis tool as an ADK FunctionTool.

    This function creates a FunctionDeclaration for the behaviour_db_tool,
    which allows the ADK agent to call it at runtime to analyze user behaviour
    and retrieve structured intervention recommendations.

    Returns:
        Tool: ADK Tool object containing the behaviour_db_tool function declaration

    Example:
        >>> tool = create_behaviour_db_function_tool()
        >>> # Pass tool to ADK agent configuration
    """
    # Define the function schema
    parameters_schema = Schema(
        type=Type.OBJECT,
        properties={
            "user_input": Schema(
                type=Type.STRING,
                description="User's description of their financial habit, struggle, or goal",
            ),
            "session_meta": Schema(
                type=Type.OBJECT,
                description="Optional session metadata with user context",
            ),
        },
        required=["user_input"],
    )

    function_declaration = FunctionDeclaration(
        name="behaviour_db_tool",
        description=(
            "Analyzes user financial habit input to detect the most relevant behavioural "
            "science principle (e.g., loss aversion, habit loops, friction increase/decrease, "
            "commitment devices, etc.) and returns structured intervention suggestions. "
            "Use this tool when you need to understand the underlying behavioural pattern "
            "in a user's financial habit or struggle."
        ),
        parameters=parameters_schema,
    )

    logger.info("Created behaviour_db_tool FunctionDeclaration")

    return Tool(function_declarations=[function_declaration])


# Module-level instance (created lazily to avoid requiring API key at import time)
_behaviour_db_function_tool = None


def get_behaviour_db_tool() -> Tool:
    """
    Get or create the behaviour DB function tool.

    Returns:
        Tool: The behaviour DB analysis tool.
    """
    global _behaviour_db_function_tool  # noqa: PLW0603
    if _behaviour_db_function_tool is None:
        _behaviour_db_function_tool = create_behaviour_db_function_tool()
    return _behaviour_db_function_tool
