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
from pathlib import Path
from typing import Any

from google.genai import Client

from src.behaviour_engine import analyse_behaviour, load_behaviour_db
from src.coach import run_once
from src.config import get_adk_model_name
from src.memory import UserMemory

logger = logging.getLogger(__name__)


class HabitLedgerAgent:
    """
    HabitLedger agent with dependency injection.

    This class provides a stateless agent instance that accepts
    behaviour database and user memory as dependencies, avoiding
    global state for better testability and multi-user support.
    """

    def __init__(self, behaviour_db: dict[str, Any], memory: UserMemory):
        """
        Initialize HabitLedger agent with dependencies.

        Args:
            behaviour_db: Dictionary containing behavioural principles.
            memory: UserMemory instance for the current user.
        """
        self.behaviour_db = behaviour_db
        self.memory = memory

    def analyse_behaviour(self, user_input: str) -> dict[str, Any]:
        """
        Analyze user input using the agent's behaviour database and memory.

        Args:
            user_input: The user's description of their financial habit situation.

        Returns:
            dict: Analysis result with detected principle and interventions.
        """
        return analyse_behaviour(user_input, self.memory, self.behaviour_db)

    def generate_response(self, user_input: str) -> str:
        """
        Generate a coaching response for user input.

        Args:
            user_input: The user's message.

        Returns:
            str: Coaching response.
        """
        return run_once(user_input, self.memory, self.behaviour_db)


# Global state for backward compatibility (single-user demo)
_behaviour_db: dict[str, Any] | None = None
_user_memory: UserMemory | None = None


def _ensure_initialized() -> tuple[UserMemory, dict[str, Any]]:
    """
    Ensure behaviour DB and user memory are initialized (legacy, for backward compatibility).

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
        from src.models import Goal

        _user_memory = UserMemory(user_id="adk_demo_user")
        _user_memory.goals = [
            Goal(description="Build better financial habits"),
            Goal(description="Control impulse spending"),
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


# Module-level instances (created lazily to avoid requiring API key at import time)
_root_agent = None


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
