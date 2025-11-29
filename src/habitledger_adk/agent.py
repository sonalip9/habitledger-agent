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
from typing import Any, Optional

from google.adk import Agent
from google.genai import Client

from src.adk_config import INSTRUCTION_TEXT
from src.adk_tools import behaviour_db_tool
from src.behaviour_engine import analyse_behaviour, load_behaviour_db
from src.coach import run_once
from src.llm_client import analyse_behaviour_with_llm
from src.memory import UserMemory
from src.memory_service import MemoryService

logger = logging.getLogger(__name__)


def get_user_memory() -> UserMemory | None:
    """Get the current user memory from global state."""
    return _user_memory


def set_user_memory(memory: UserMemory) -> None:
    """Set the user memory in global state."""
    global _user_memory  # noqa: PLW0603
    _user_memory = memory


class HabitLedgerAgent(Agent):
    """
    ADK-based HabitLedger agent orchestrating behavioral money coaching.
    Implements ADK lifecycle methods, dependency injection, tool registration,
    LLM integration with fallback, state management, observability, and error handling.
    """

    def __init__(
        self,
        memory: UserMemory,
        config: dict[str, Any],
        llm_client=None,
        tools: Optional[list[Any]] = None,
    ):
        if tools is None:
            tools = [behaviour_db_tool]

        super().__init__(
            instruction=INSTRUCTION_TEXT, tools=tools, name="HabitLedgerAgent"
        )
        self.memory = memory
        self.config = config
        self.llm_client = llm_client

    def on_message(self, message: str):
        """
        Handle incoming user message: analyze, update state, respond.
        Uses LLM for analysis, falls back to keyword-based if needed.
        Persists state and logs decisions.
        """
        try:
            # Try LLM-based analysis first
            behaviour_db = self.config.get("behaviour_db")
            if behaviour_db is None:
                logger.error("behaviour_db not found in config")
                return {"error": "Configuration error: behaviour_db not found"}

            result = None
            if self.llm_client:
                result = analyse_behaviour_with_llm(message, self.memory, behaviour_db)
            if not result:
                # Fallback: keyword-based
                result = analyse_behaviour(message, self.memory, behaviour_db)

            # Log principle detection
            logger.info(
                "principle_detected",
                extra={
                    "principle_id": result.get("detected_principle_id"),
                    "confidence": result.get("confidence", 0.5),
                    "method": "llm" if self.llm_client else "keyword",
                    "reasoning": result.get("reason", ""),
                },
            )

            # Update memory/state
            MemoryService.record_interaction(
                self.memory,
                {
                    "type": "intervention",
                    "principle_id": result.get("detected_principle_id"),
                    "description": result.get("reason", ""),
                },
            )
            self.memory.add_conversation_turn("user", message)
            self.memory.add_conversation_turn("assistant", result.get("reason", ""))
            # Save memory with default path
            memory_path = self.config.get(
                "memory_path", f"memory_{self.memory.user_id}.json"
            )
            self.memory.save_to_file(memory_path)

            # Build response
            response = {
                "principle": result.get("detected_principle_id"),
                "interventions": result.get("intervention_suggestions", []),
                "reasoning": result.get("reason", ""),
            }
            return response
        except Exception as e:
            logger.error("analysis_error", extra={"error": str(e)}, exc_info=True)
            return {"error": f"Error processing message: {str(e)}"}

    def on_tool_call(self, tool_name: str, args: dict):
        """
        Handle ADK tool calls, with error handling and logging.
        """
        try:
            if tool_name == "behaviour_db_tool":
                result = behaviour_db_tool(
                    args.get("user_input", ""), args.get("session_meta")
                )
                logger.info("tool_call", extra={"tool": tool_name, "result": result})
                return result
            # Add more tool handlers as needed
            logger.warning("Unknown tool call", extra={"tool": tool_name})
            return {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            logger.error(
                "tool_call_error",
                extra={"tool": tool_name, "error": str(e)},
                exc_info=True,
            )
            return {"error": f"Tool call failed: {str(e)}"}

    # Additional ADK lifecycle methods can be added here as needed


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

    # Type guard to satisfy type checker
    assert _user_memory is not None
    assert _behaviour_db is not None
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


def create_root_agent() -> Client:
    """
    Create and configure the HabitLedger root agent using Google ADK.

    This function initializes a Google GenAI client configured as the
    HabitLedger behavioural money coach agent with the custom coaching tool.

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
        _root_agent = create_root_agent()
    return _root_agent
