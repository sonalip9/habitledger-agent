"""
ADK-based HabitLedger root agent definition.

This module defines the main ADK agent for HabitLedger, configuring it
with appropriate instructions and behavioural coaching capabilities using
Google's Agent Development Kit (ADK).

This module implements proper dependency injection for multi-user support
and testability. All dependencies (memory, behaviour_db) are passed explicitly
through function parameters rather than relying on global state.
"""

import logging
from typing import Any, Optional

from google.adk import Agent

from src.adk_config import INSTRUCTION_TEXT
from src.adk_tools import behaviour_db_tool
from src.behaviour_engine import analyse_behaviour
from src.coach import run_once
from src.llm_client import analyse_behaviour_with_llm
from src.memory import UserMemory
from src.memory_service import MemoryService

logger = logging.getLogger(__name__)


class HabitLedgerAgent(Agent):
    """
    ADK-based HabitLedger agent orchestrating behavioral money coaching.
    Implements ADK lifecycle methods, dependency injection, tool registration,
    LLM integration with fallback, state management, observability, and error handling.
    """

    def __init__(
        self,
        memory: UserMemory,
        behaviour_db: dict[str, Any],
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
        self.behaviour_db = behaviour_db
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
            result = None
            if self.llm_client:
                result = analyse_behaviour_with_llm(
                    message, self.memory, self.behaviour_db
                )
            if not result:
                # Fallback: keyword-based
                result = analyse_behaviour(message, self.memory, self.behaviour_db)

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


def habitledger_coach_tool(
    user_input: str, memory: UserMemory, behaviour_db: dict[str, Any]
) -> dict[str, str]:
    """
    Run the core HabitLedger coaching flow for a single user input.

    This function serves as the ADK tool wrapper around HabitLedger's
    core coaching logic. It analyzes user input, detects behavioural patterns,
    and provides personalized coaching responses with interventions.

    Args:
        user_input: The user's free-text description of their financial habit situation.
        memory: UserMemory instance for the current user session.
        behaviour_db: Behaviour principles database.

    Returns:
        dict: A dictionary with keys:
            - "response": str, the coach's textual reply with principle detection
              and interventions
            - "status": str, status indicator ("success" or "error")

    Example:
        >>> memory = UserMemory(user_id="user123")
        >>> behaviour_db = load_behaviour_db("path/to/db.json")
        >>> result = habitledger_coach_tool("I keep ordering food delivery", memory, behaviour_db)
        >>> print(result["response"])
        🎯 Detected Principle: Friction Increase...
    """
    try:
        response = run_once(user_input, memory, behaviour_db)
        return {"response": response, "status": "success"}
    except Exception as e:  # noqa: BLE001
        return {"response": f"Error processing request: {str(e)}", "status": "error"}


def create_root_agent(
    memory: UserMemory,
    behaviour_db: dict[str, Any],
    config: Optional[dict[str, Any]] = None,
) -> HabitLedgerAgent:
    """
    Create and configure the HabitLedger root agent using Google ADK.

    This function initializes a HabitLedgerAgent with proper dependency injection
    for multi-user support and testability.

    Args:
        memory: UserMemory instance for the user session.
        behaviour_db: Behaviour principles database.
        config: Optional configuration dictionary.

    Returns:
        HabitLedgerAgent: Configured HabitLedger agent instance

    Example:
        >>> memory = UserMemory(user_id="user123")
        >>> behaviour_db = load_behaviour_db("path/to/db.json")
        >>> agent = create_root_agent(memory, behaviour_db)
        >>> # Use agent for coaching interactions
    """
    if config is None:
        config = {}

    return HabitLedgerAgent(
        memory=memory,
        behaviour_db=behaviour_db,
        config=config,
    )
