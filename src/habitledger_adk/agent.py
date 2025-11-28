"""
ADK-based HabitLedger root agent definition.

This module defines the main ADK agent for HabitLedger, configuring it
with appropriate instructions and behavioural coaching capabilities using
Google's Agent Development Kit (ADK).

Note: This module uses global memory state for simplicity in the demo.
For production with ADK Runner integration, use the session-based memory
management provided in runner.py which integrates with ADK's native
session services (DatabaseSessionService).
"""

import logging
import sys
from pathlib import Path
from typing import Any

from google.genai import Client
from google.genai.types import FunctionDeclaration, Schema, Tool, Type

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from src.behaviour_engine import analyse_behaviour
from src.coach import load_behaviour_db, run_once
from src.config import get_adk_model_name
from src.memory import MAX_CONVERSATION_CONTEXT_LENGTH, UserMemory

logger = logging.getLogger(__name__)

# Agent instruction text
INSTRUCTION_TEXT = """You are a behavioural finance coach named HabitLedger.

Your role is to help users build sustainable financial habits including:
- SIP (Systematic Investment Plan) consistency
- Budgeting and expense tracking
- Impulse control and mindful spending
- Building emergency funds and long-term savings

You use principles from behavioural science such as:
- Loss aversion
- Habit loops and trigger identification
- Commitment devices
- Temptation bundling
- Friction reduction/increase
- Default effects
- Micro-habits and small wins

Guidelines:
1. Ask clarifying questions when users describe vague situations
2. Keep recommendations practical and actionable
3. Suggest small, incremental changes rather than overwhelming overhauls
4. Use empathy and encouragement - avoid judgment
5. Reference specific behavioural principles when explaining "why" something works
6. Help users identify triggers and patterns in their spending behavior

Always be supportive, understanding, and focused on sustainable habit change."""

# Global state for memory and behaviour DB (single-user demo)
_behaviour_db: dict[str, Any] | None = None
_user_memory: UserMemory | None = None


def _ensure_initialized() -> tuple[UserMemory, dict[str, Any]]:
    """
    Ensure behaviour DB and user memory are initialized.

    Returns:
        tuple: (user_memory, behaviour_db)
    """
    global _behaviour_db, _user_memory  # noqa: PLW0603

    if _behaviour_db is None:
        db_path = (
            Path(__file__).parent.parent.parent / "data" / "behaviour_principles.json"
        )
        _behaviour_db = load_behaviour_db(str(db_path))

    if _user_memory is None:
        _user_memory = UserMemory(user_id="adk_demo_user")
        _user_memory.goals = [
            {"description": "Build better financial habits"},
            {"description": "Control impulse spending"},
        ]

    return _user_memory, _behaviour_db


def behaviour_db_tool(
    user_input: str, session_meta: dict[str, Any] | None = None
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
    import time

    start_time = time.time()
    user_input_truncated = user_input[:MAX_CONVERSATION_CONTEXT_LENGTH] if len(user_input) > MAX_CONVERSATION_CONTEXT_LENGTH else user_input

    try:
        memory, behaviour_db = _ensure_initialized()

        # Run behaviour analysis (will try ADK first, fall back to keyword)
        analysis_result = analyse_behaviour(user_input, memory, behaviour_db)

        principle_id = analysis_result.get("detected_principle_id")
        interventions = analysis_result.get("intervention_suggestions", [])
        reason = analysis_result.get("reason", "")
        source = analysis_result.get("source", "unknown")

        # Build structured response
        explanation = (
            f"Detected principle: {principle_id or 'None'}. {reason} (Source: {source})"
        )

        duration_ms = int((time.time() - start_time) * 1000)

        logger.info(
            "behaviour_db_tool executed",
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


def habitledger_coach_tool(user_input: str) -> dict[str, str]:
    """
    Run the core HabitLedger coaching flow for a single user input.

    This function serves as the ADK tool wrapper around HabitLedger's
    core coaching logic. It analyzes user input, detects behavioural patterns,
    and provides personalized coaching responses with interventions.

    Args:
        user_input: The user's free-text description of their financial habit situation.

    Returns:
        dict: A dictionary with keys:
            - "response": str, the coach's textual reply with principle detection
              and interventions
            - "status": str, status indicator ("success" or "error")

    Example:
        >>> result = habitledger_coach_tool("I keep ordering food delivery")
        >>> print(result["response"])
        🎯 Detected Principle: Friction Increase...
    """
    try:
        memory, behaviour_db = _ensure_initialized()
        response = run_once(user_input, memory, behaviour_db)

        return {"response": response, "status": "success"}
    except Exception as e:  # noqa: BLE001
        return {"response": f"Error processing request: {str(e)}", "status": "error"}


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


def create_root_agent(
    model_name: str = "gemini-2.0-flash-exp",
) -> Client:  # noqa: ARG001
    """
    Create and configure the HabitLedger root agent using Google ADK.

    This function initializes a Google GenAI client configured as the
    HabitLedger behavioural money coach agent with the custom coaching tool.

    Args:
        model_name: The model to use for the agent (default: "gemini-2.0-flash-exp")
                    Reserved for future use when configuring model-specific settings.

    Returns:
        Client: Configured Google GenAI client acting as the HabitLedger agent

    Example:
        >>> agent = create_root_agent()
        >>> # Use agent for coaching interactions
    """
    # Note: model_name will be used in future when creating agent instances
    # with specific model configurations

    # Initialize client (tools will be configured when used)
    client = Client()
    return client


# Module-level instances (created lazily to avoid requiring API key at import time)
_root_agent = None
_behaviour_db_function_tool = None


def get_root_agent() -> Client:
    """
    Get or create the default root agent instance.

    Returns:
        Client: The configured HabitLedger agent client.
    """
    global _root_agent  # noqa: PLW0603
    if _root_agent is None:
        _root_agent = create_root_agent(model_name=get_adk_model_name())
    return _root_agent


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
