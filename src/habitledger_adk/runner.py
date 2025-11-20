"""
Runner utilities for the HabitLedger ADK agent.

This module provides runner functionality to execute the HabitLedger agent
in various modes, including a simple CLI for local testing and demonstration.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google.genai import Client
from google.genai.types import (
    GenerateContentConfig,
    Tool,
    FunctionDeclaration,
    Schema,
    Type,
)

from src.config import get_adk_model_name, get_api_key, setup_logging
from .agent import habitledger_coach_tool, INSTRUCTION_TEXT


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


def run_cli() -> None:
    """
    Run the HabitLedger ADK agent in a simple CLI loop.

    This function provides a basic command-line interface for interacting
    with the HabitLedger agent. It's primarily for local testing and demos.

    The CLI accepts user input, sends it to the agent with tool support,
    and displays the coaching responses.

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
        # Initialize client
        api_key = get_api_key()
        client = Client(api_key=api_key)
        model_name = get_adk_model_name()

        # Create tool
        habitledger_tool = create_habitledger_tool()

        print(f"✅ Using model: {model_name}")
        print("✅ HabitLedger coaching tool loaded\n")
        print("-" * 70)

        # Main interaction loop
        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print(
                        "\n👋 Thanks for using HabitLedger! Keep building those healthy habits!"
                    )
                    break

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
                            print("\n🤖 Coach (via tool):")
                            print(tool_result["response"])
                        elif hasattr(part, "text") and part.text:
                            # Direct text response
                            print(f"\n🤖 Coach:\n{part.text}")
                        else:
                            print("\n🤖 Coach: [No response generated]")
                else:
                    print("\n🤖 Coach: [No response generated]")

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
