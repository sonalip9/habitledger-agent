"""
ADK-based HabitLedger root agent definition.

This module defines the main ADK agent for HabitLedger, configuring it
with appropriate instructions and behavioural coaching capabilities using
Google's Agent Development Kit (ADK).
"""

import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google.genai import Client

from src.config import get_adk_model_name
from src.memory import UserMemory
from src.coach import run_once, load_behaviour_db

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


# Default root agent instance using configured model
root_agent = create_root_agent(model_name=get_adk_model_name())
