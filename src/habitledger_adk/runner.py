"""
Runner utilities for the HabitLedger ADK agent.

This module provides runner functionality to execute the HabitLedger agent
in various modes, including a simple CLI for local testing and demonstration.

Uses Google ADK's native InMemorySessionService for session management.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from google.adk.sessions import Session
from google.genai import Client
from google.genai.types import (
    FunctionDeclaration,
    GenerateContentConfig,
    Schema,
    Tool,
    Type,
)

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from src.config import get_adk_model_name, get_api_key, setup_logging
from src.memory import UserMemory
from src.session_db import create_session_service

from .agent import INSTRUCTION_TEXT, habitledger_coach_tool

logger = logging.getLogger(__name__)


# ADK Session State Keys
STATE_USER_MEMORY = "user:memory"  # User-scoped: persists across sessions
STATE_CONVERSATION_COUNT = "conversation_count"  # Session-scoped


def save_memory_to_session(session: Session, user_memory: UserMemory) -> None:
    """
    Save UserMemory to ADK session state.

    Uses the 'user:' prefix to ensure memory persists across all sessions
    for this user.

    Args:
        session: ADK Session object.
        user_memory: UserMemory instance to serialize and save.

    Example:
        >>> session = session_service.get_session_sync(session_id="sess123")
        >>> memory = UserMemory(user_id="user123")
        >>> save_memory_to_session(session, memory)
    """
    memory_dict = user_memory.to_dict()
    session.state[STATE_USER_MEMORY] = memory_dict

    logger.info(
        "Memory saved to session state",
        extra={
            "event": "session_memory_save",
            "session_id": session.id,
            "user_id": user_memory.user_id,
            "goals_count": len(user_memory.goals),
            "active_streaks": sum(
                1 for s in user_memory.streaks.values() if s.get("current", 0) > 0
            ),
            "total_streaks": len(user_memory.streaks),
            "struggles_count": len(user_memory.struggles),
            "conversation_turns": len(user_memory.conversation_history),
        },
    )


def load_memory_from_session(session: Session) -> Optional[UserMemory]:
    """
    Load UserMemory from ADK session state.

    Args:
        session: ADK Session object.

    Returns:
        UserMemory or None: Loaded UserMemory instance if found, None otherwise.

    Example:
        >>> session = session_service.get_session_sync(session_id="sess123")
        >>> memory = load_memory_from_session(session)
    """
    memory_dict = session.state.get(STATE_USER_MEMORY)
    if memory_dict:
        return UserMemory.from_dict(memory_dict)
    return None


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


def create_runner(
    user_id: str = "demo_user",
):
    """
    Create an ADK runner with session management.

    This function initializes a Google GenAI client and creates an
    InMemorySessionService for session state management.

    Args:
        user_id: User identifier for the session (default: "demo_user").

    Returns:
        tuple: (client, session_service, session) - The configured client,
               session service, and the Session object.

    Example:
        >>> client, service, session = create_runner("user123")
        >>> memory = load_memory_from_session(session)
        >>> print(memory.user_id)
        user123
    """
    # Initialize client
    api_key = get_api_key()
    client = Client(api_key=api_key)

    # Check if session already exists for this user
    session_id = f"session_{user_id}"
    app_name = "habitledger"

    # Create session service using ADK's InMemorySessionService
    session_service = create_session_service()

    try:
        session = session_service.get_session_sync(
            session_id=session_id,
            app_name=app_name,
            user_id=user_id,
        )
        logger.info(
            "Existing session loaded",
            extra={"user_id": user_id, "session_id": session_id},
        )
    except Exception:
        # Session doesn't exist, create new one
        session = session_service.create_session_sync(
            session_id=session_id,
            app_name=app_name,
            user_id=user_id,
        )

        # Initialize user memory and save to session
        user_memory = UserMemory(user_id=user_id)
        user_memory.goals = [
            {"description": "Build better financial habits"},
            {"description": "Control impulse spending"},
        ]
        save_memory_to_session(session, user_memory)

        logger.info(
            "New session created",
            extra={"user_id": user_id, "session_id": session_id},
        )

    return client, session_service, session


def run_cli() -> None:
    """
    Run the HabitLedger ADK agent in a simple CLI loop with session persistence.

    This function provides a command-line interface for interacting with the
    HabitLedger agent. It uses ADK's DatabaseSessionService to maintain session
    state with full persistence across application restarts.

    The CLI accepts user input, sends it to the agent with tool support,
    displays coaching responses, and updates session memory after each turn.
    Session events are automatically tracked by the ADK session service.

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
        # Create runner with ADK session service
        client, session_service, session = create_runner(user_id="cli_demo_user")
        model_name = get_adk_model_name()

        # Create tool
        habitledger_tool = create_habitledger_tool()

        print(f"✅ Using model: {model_name}")
        print("✅ HabitLedger coaching tool loaded")
        print(f"✅ Session initialized: {session.id}")
        print(f"✅ Session service: {type(session_service).__name__}\n")
        print("-" * 70)

        # Main interaction loop
        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye"]:
                    # Load final memory state
                    user_memory = load_memory_from_session(session)
                    if user_memory:
                        logger.info(
                            "Session ending",
                            extra={
                                "session_id": session.id,
                                "total_interventions": len(user_memory.interventions),
                                "total_events": len(session.events),
                            },
                        )
                    print(
                        "\n👋 Thanks for using HabitLedger! Keep building those healthy habits!"
                    )
                    break

                # Load current memory from session
                user_memory = load_memory_from_session(session)

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

                # Note: session_service.append_event() is async and requires await
                # For now, we rely on conversation_history in UserMemory for tracking

                # Update and save memory back to session
                if user_memory:
                    # Memory is already updated by habitledger_coach_tool
                    save_memory_to_session(session, user_memory)

                    # Increment conversation counter
                    count = session.state.get(STATE_CONVERSATION_COUNT, 0)
                    session.state[STATE_CONVERSATION_COUNT] = count + 1

                    logger.info(
                        "Session interaction complete",
                        extra={
                            "event": "session_interaction",
                            "session_id": session.id,
                            "user_id": session.user_id,
                            "interventions": len(user_memory.interventions),
                            "conversation_turns": count + 1,
                            "response_length": (
                                len(agent_response) if agent_response else 0
                            ),
                            "session_events": len(session.events),
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
                logger.error("CLI interaction error", exc_info=True)

    except Exception as e:  # noqa: BLE001
        print(f"\n❌ Initialization error: {e}")
        print("Please check your configuration and try again.")
        logger.error("CLI initialization error", exc_info=True)
        return


if __name__ == "__main__":
    run_cli()
