"""
Core agent logic & interaction flow.

This module contains the main HabitLedger coach agent that orchestrates
user interactions, coordinates behaviour analysis, and generates coaching responses.
It serves as the central controller that ties together memory management,
behaviour analysis, and response generation.
"""

import json
from pathlib import Path
from typing import Any

from .behaviour_engine import analyse_behaviour
from .memory import UserMemory


def load_behaviour_db(path: str) -> dict[str, Any]:
    """
    Load the behaviour principles database from a JSON file.

    Args:
        path: Path to the behaviour_principles.json file.

    Returns:
        dict: The loaded behaviour database containing principles and interventions.

    Raises:
        FileNotFoundError: If the database file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.

    Example:
        >>> db = load_behaviour_db("data/behaviour_principles.json")
        >>> print(len(db["principles"]))
        8
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Behaviour database not found: {path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_once(
    user_input: str,
    memory: UserMemory,
    behaviour_db: dict[str, Any],
) -> str:
    """
    Process a single user interaction and generate a coaching response.

    This function orchestrates the core agent loop for one interaction:
    1. Analyzes user input to detect relevant behavioural principles
    2. Generates a personalized coaching response with interventions
    3. Updates user memory with the interaction outcome

    Args:
        user_input: The user's message or description of their situation.
        memory: UserMemory instance to track user state across interactions.
        behaviour_db: Dictionary containing behavioural principles.

    Returns:
        str: A coaching response summarizing the detected principle and suggesting
             an intervention, or general guidance if no principle was detected.

    Example:
        >>> memory = UserMemory(user_id="user123")
        >>> db = load_behaviour_db("data/behaviour_principles.json")
        >>> response = run_once("I keep ordering food delivery", memory, db)
        >>> print(response)
        🎯 Detected Principle: Friction Increase (Make Bad Habits Hard)...
    """
    # Step 1: Analyze user behaviour
    analysis = analyse_behaviour(user_input, memory, behaviour_db)

    detected_principle_id = analysis.get("detected_principle_id")
    reason = analysis.get("reason", "")
    interventions = analysis.get("intervention_suggestions", [])

    # Step 2: Build response
    response_parts = []

    if detected_principle_id:
        # Find principle name for display
        principles = behaviour_db.get("principles", [])
        principle_data = next(
            (p for p in principles if p.get("id") == detected_principle_id),
            None,
        )
        principle_name = (
            principle_data.get("name", detected_principle_id)
            if principle_data
            else detected_principle_id
        )

        response_parts.append(f"🎯 **Detected Principle:** {principle_name}\n")
        response_parts.append(f"💡 **Why:** {reason}\n")

        if interventions:
            response_parts.append(f"\n✨ **Suggested Action:**\n{interventions[0]}\n")

            if len(interventions) > 1:
                response_parts.append("\n📝 **More Ideas:**")
                for i, intervention in enumerate(interventions[1:3], 1):
                    response_parts.append(f"\n{i}. {intervention}")
    else:
        response_parts.append("💬 **General Guidance**\n")
        response_parts.append(f"{reason}\n")

        if interventions:
            response_parts.append("\n✨ **Suggestions:**")
            for i, intervention in enumerate(interventions[:3], 1):
                response_parts.append(f"\n{i}. {intervention}")

    # Step 3: Update memory
    # Record this as an intervention if a principle was detected
    if detected_principle_id and interventions:
        memory.record_interaction(
            {
                "type": "intervention",
                "principle_id": detected_principle_id,
                "description": interventions[0],
            }
        )

    # Step 4: Return formatted response
    return "".join(response_parts)


def main() -> None:
    """
    Run the HabitLedger coach in interactive command-line mode.

    This function provides a simple REPL (Read-Eval-Print Loop) interface
    for testing and demonstrating the coach agent. It:
    - Loads the behaviour principles database
    - Initializes user memory
    - Continuously prompts for user input
    - Processes each input through the agent
    - Displays coaching responses
    - Exits when user types "quit"

    The memory is kept in-memory only and is not persisted between sessions.

    Example:
        Run from command line:
        $ python -m src.coach

        Then interact:
        > I keep ordering food delivery when stressed
        [Agent responds with principle and intervention]
        > quit
        Goodbye!
    """
    print("=" * 60)
    print("🌟 Welcome to HabitLedger - Your Behavioural Money Coach")
    print("=" * 60)
    print("\nI'm here to help you build better financial habits.")
    print("Share your struggles, goals, or check in on your progress.")
    print("\nType 'quit' to exit.\n")

    # Load behaviour database
    try:
        db_path = Path(__file__).parent.parent / "data" / "behaviour_principles.json"
        behaviour_db = load_behaviour_db(str(db_path))
        print(
            f"✅ Loaded {len(behaviour_db.get('principles', []))} behavioural principles\n"
        )
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Please ensure behaviour_principles.json exists in the data/ directory.")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing behaviour database: {e}")
        return

    # Initialize memory (in-memory for now)
    memory = UserMemory(user_id="demo_user")
    print("✅ Memory initialized\n")
    print("-" * 60)

    # Main interaction loop
    while True:
        try:
            user_input = input("\n💬 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "bye"]:
                print("\n👋 Goodbye! Keep building those healthy habits!")
                break

            # Process user input
            response = run_once(user_input, memory, behaviour_db)

            print(f"\n🤖 Coach:\n{response}")
            print("\n" + "-" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Keep building those healthy habits!")
            break
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try again or type 'quit' to exit.\n")


if __name__ == "__main__":
    main()
