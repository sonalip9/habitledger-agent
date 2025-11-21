"""
Runner utilities for the HabitLedger ADK agent.

This module provides runner functionality to execute the HabitLedger agent
in various modes, including a simple CLI for local testing and demonstration.
"""

import logging
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google.genai import Client
from google.genai.types import (
    FunctionDeclaration,
    GenerateContentConfig,
    Schema,
    Tool,
    Type,
)

from src.config import get_adk_model_name, get_api_key, setup_logging
from src.memory import UserMemory

from .agent import INSTRUCTION_TEXT, habitledger_coach_tool

logger = logging.getLogger(__name__)


def create_habitledger_tool() -> Tool:
    """
    Create the HabitLedger coaching tool for ADK agent.

    Returns:
        Tool: Configured tool with habitledger_coach function declaration

    Example:
        >>> tool = create_habitledger_tool()
        >>> # Use tool with ADK agent
    """
    # Create schema for parameters
    parameters_schema = Schema(
        type=Type.OBJECT,
        properties={
            "user_input": Schema(
                type=Type.STRING,
                description="The user's description of their financial habit, struggle, or goal",
            )
        },
        required=["user_input"],
    )

    function_declaration = FunctionDeclaration(
        name="habitledger_coach",
        description=(
            "Analyzes user's financial habit situation and provides behavioural coaching. "
            "Detects underlying behavioural patterns (e.g., loss aversion, habit loops, "
            "friction issues) and suggests evidence-based interventions to build better habits."
        ),
        parameters=parameters_schema,
    )

    return Tool(function_declarations=[function_declaration])


class InMemorySessionService:
    """
    In-memory session storage service for the ADK agent.

    This service provides a simple in-memory storage mechanism for managing
    session state across interactions. It stores session metadata including
    user memory and conversation history.

    Attributes:
        sessions (dict): Dictionary mapping session_id to session data.

    Example:
        >>> service = InMemorySessionService()
        >>> service.create_session("user123", {"user_memory": {...}})
        >>> session = service.get_session("user123")
    """

    def __init__(self) -> None:
        """Initialize the in-memory session storage."""
        self.sessions: dict[str, dict[str, Any]] = {}

    def create_session(
        self, session_id: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Create a new session with optional metadata.

        Args:
            session_id: Unique identifier for the session.
            metadata: Optional initial metadata for the session.

        Example:
            >>> service = InMemorySessionService()
            >>> service.create_session("user123", {"user_id": "user123"})
        """
        self.sessions[session_id] = {
            "session_id": session_id,
            "metadata": metadata or {},
            "history": [],
        }
        logger.info("Session created", extra={"session_id": session_id})

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        Retrieve session data by ID.

        Args:
            session_id: The session identifier.

        Returns:
            dict or None: Session data if found, None otherwise.

        Example:
            >>> service = InMemorySessionService()
            >>> service.create_session("user123")
            >>> session = service.get_session("user123")
            >>> print(session["session_id"])
            user123
        """
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, metadata: dict[str, Any]) -> None:
        """
        Update session metadata.

        Args:
            session_id: The session identifier.
            metadata: New or updated metadata to merge with existing data.

        Example:
            >>> service = InMemorySessionService()
            >>> service.create_session("user123")
            >>> service.update_session("user123", {"last_interaction": "2025-11-21"})
        """
        if session_id in self.sessions:
            self.sessions[session_id]["metadata"].update(metadata)
            logger.info("Session updated", extra={"session_id": session_id})

    def add_to_history(self, session_id: str, entry: dict[str, Any]) -> None:
        """
        Add an entry to the session history.

        Args:
            session_id: The session identifier.
            entry: History entry to add (e.g., user input and response).

        Example:
            >>> service = InMemorySessionService()
            >>> service.create_session("user123")
            >>> service.add_to_history("user123", {"user": "Hello", "agent": "Hi!"})
        """
        if session_id in self.sessions:
            self.sessions[session_id]["history"].append(entry)

    def save_memory_to_session(self, session_id: str, user_memory: UserMemory) -> None:
        """
        Save UserMemory to session metadata.

        Args:
            session_id: The session identifier.
            user_memory: UserMemory instance to serialize and save.

        Example:
            >>> service = InMemorySessionService()
            >>> memory = UserMemory(user_id="user123")
            >>> service.create_session("user123")
            >>> service.save_memory_to_session("user123", memory)
        """
        memory_dict = user_memory.to_dict()
        self.update_session(session_id, {"user_memory": memory_dict})
        logger.info(
            "Memory saved to session",
            extra={"session_id": session_id, "user_id": user_memory.user_id},
        )

    def load_memory_from_session(self, session_id: str) -> UserMemory | None:
        """
        Load UserMemory from session metadata.

        Args:
            session_id: The session identifier.

        Returns:
            UserMemory or None: Loaded UserMemory instance if found, None otherwise.

        Example:
            >>> service = InMemorySessionService()
            >>> service.create_session("user123", {"user_memory": {...}})
            >>> memory = service.load_memory_from_session("user123")
        """
        session = self.get_session(session_id)
        if session and "user_memory" in session["metadata"]:
            memory_dict = session["metadata"]["user_memory"]
            return UserMemory.from_dict(memory_dict)
        return None


def create_runner(
    user_id: str = "demo_user",
) -> tuple[Client, InMemorySessionService, str]:
    """
    Create an ADK runner with InMemorySessionService.

    This function initializes a Google GenAI client, creates an in-memory
    session service, and sets up a session for the specified user with
    an initialized UserMemory.

    Args:
        user_id: User identifier for the session (default: "demo_user").

    Returns:
        tuple: (client, session_service, session_id) - The configured client,
               session service, and the created session ID.

    Example:
        >>> client, service, session_id = create_runner("user123")
        >>> memory = service.load_memory_from_session(session_id)
        >>> print(memory.user_id)
        user123
    """
    # Initialize client
    api_key = get_api_key()
    client = Client(api_key=api_key)

    # Create session service
    session_service = InMemorySessionService()

    # Create session for user
    session_id = f"session_{user_id}"
    session_service.create_session(session_id)

    # Initialize user memory and save to session
    user_memory = UserMemory(user_id=user_id)
    user_memory.goals = [
        {"description": "Build better financial habits"},
        {"description": "Control impulse spending"},
    ]
    session_service.save_memory_to_session(session_id, user_memory)

    logger.info(
        "Runner created",
        extra={"user_id": user_id, "session_id": session_id},
    )

    return client, session_service, session_id


def run_cli() -> None:
    """
    Run the HabitLedger ADK agent in a simple CLI loop with session persistence.

    This function provides a command-line interface for interacting with the
    HabitLedger agent. It uses InMemorySessionService to maintain session state
    and persist UserMemory across interactions within the same session.

    The CLI accepts user input, sends it to the agent with tool support,
    displays coaching responses, and updates session memory after each turn.

    Example:
        Run from command line:
        $ python -m src.habitledger_adk.runner
    """
    # Set up logging
    setup_logging()
    print("=" * 70)
    print("🌟 HabitLedger ADK Agent - Interactive CLI")
    print("=" * 70)
    print("\nI'm your AI-powered behavioural money coach.")
    print("Share your financial habits, struggles, or goals, and I'll help!")
    print("\nType 'quit' to exit.\n")

    try:
        # Create runner with session service
        client, session_service, session_id = create_runner(user_id="cli_demo_user")
        model_name = get_adk_model_name()

        # Create tool
        habitledger_tool = create_habitledger_tool()

        print(f"✅ Using model: {model_name}")
        print("✅ HabitLedger coaching tool loaded")
        print(f"✅ Session initialized: {session_id}\n")
        print("-" * 70)

        # Main interaction loop
        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye"]:
                    # Save final session state
                    user_memory = session_service.load_memory_from_session(session_id)
                    if user_memory:
                        logger.info(
                            "Session ending",
                            extra={
                                "session_id": session_id,
                                "total_interventions": len(user_memory.interventions),
                            },
                        )
                    print(
                        "\n👋 Thanks for using HabitLedger! Keep building those healthy habits!"
                    )
                    break

                # Load current memory from session
                user_memory = session_service.load_memory_from_session(session_id)

                # Generate response with tool calling
                config = GenerateContentConfig(
                    system_instruction=INSTRUCTION_TEXT,
                    tools=[habitledger_tool],
                    temperature=0.7,
                )

                # First call - let model decide to use tool
                response = client.models.generate_content(
                    model=model_name, contents=user_input, config=config
                )

                # Check if model wants to call the tool
                agent_response = None
                if (
                    response.candidates
                    and response.candidates[0].content
                    and response.candidates[0].content.parts
                ):
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "function_call") and part.function_call:
                            # Execute the tool
                            args = (
                                part.function_call.args
                                if part.function_call.args
                                else {}
                            )
                            tool_input = (
                                args.get("user_input", user_input)
                                if hasattr(args, "get")
                                else user_input
                            )
                            tool_result = habitledger_coach_tool(tool_input)

                            # Send tool result back to model
                            agent_response = tool_result["response"]
                            print("\n🤖 Coach (via tool):")
                            print(agent_response)
                        elif hasattr(part, "text") and part.text:
                            # Direct text response
                            agent_response = part.text
                            print(f"\n🤖 Coach:\n{agent_response}")
                        else:
                            print("\n🤖 Coach: [No response generated]")
                else:
                    print("\n🤖 Coach: [No response generated]")

                # Add to session history
                if agent_response:
                    session_service.add_to_history(
                        session_id,
                        {"user_input": user_input, "agent_response": agent_response},
                    )

                # Update and save memory back to session
                if user_memory:
                    # Memory is already updated by habitledger_coach_tool
                    session_service.save_memory_to_session(session_id, user_memory)
                    logger.info(
                        "Session state saved",
                        extra={
                            "session_id": session_id,
                            "interactions": len(user_memory.interventions),
                        },
                    )

                print("\n" + "-" * 70)

            except KeyboardInterrupt:
                print(
                    "\n\n👋 Thanks for using HabitLedger! Keep building those healthy habits!"
                )
                break
            except Exception as e:  # noqa: BLE001
                print(f"\n❌ Error: {e}")
                print("Please try again or type 'quit' to exit.\n")

    except Exception as e:  # noqa: BLE001
        print(f"\n❌ Initialization error: {e}")
        print("Please check your configuration and try again.")
        return


if __name__ == "__main__":
    run_cli()
