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

from .behaviour_engine import analyse_behaviour, explain_principle
from .config import setup_logging
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

        # Add behavioural explanation
        explanation = explain_principle(detected_principle_id, behaviour_db)
        response_parts.append(f"\n{explanation}\n")

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


def generate_session_summary(memory: UserMemory) -> str:
    """
    Generate a summary of the user's current session and progress.

    This function creates a comprehensive summary including current streaks,
    recent struggles, detected behavioural patterns, and an encouraging message
    to motivate continued progress.

    Args:
        memory: UserMemory instance containing user's goals, streaks, and history.

    Returns:
        str: A formatted session summary with streaks, struggles, patterns,
             and encouragement.

    Example:
        >>> memory = UserMemory(user_id="user123")
        >>> memory.streaks = {"no_food_delivery": {"current": 5, "best": 10}}
        >>> summary = generate_session_summary(memory)
        >>> print(summary)
        📊 Session Summary
        ...
    """
    summary_parts = []
    summary_parts.append("📊 **Session Summary**\n")
    summary_parts.append("=" * 50 + "\n")

    # Current streaks
    if memory.streaks:
        summary_parts.append("\n🔥 **Active Streaks:**\n")
        for streak_name, streak_data in memory.streaks.items():
            current = streak_data.get("current", 0)
            best = streak_data.get("best", 0)
            streak_label = streak_name.replace("_", " ").title()

            if current > 0:
                summary_parts.append(
                    f"  • {streak_label}: {current} days (Best: {best} days) 🎯\n"
                )
            else:
                summary_parts.append(
                    f"  • {streak_label}: Reset (Best: {best} days) - You can rebuild! 💪\n"
                )
    else:
        summary_parts.append(
            "\n🔥 **Streaks:** No active streaks yet. Start building one today!\n"
        )

    # Recent struggles
    if memory.struggles:
        summary_parts.append("\n⚠️  **Recent Struggles:**\n")
        # Show top 3 most frequent struggles
        sorted_struggles = sorted(
            memory.struggles,
            key=lambda s: s.get("count", 0),
            reverse=True,
        )[:3]

        for struggle in sorted_struggles:
            description = struggle.get("description", "Unknown")
            count = struggle.get("count", 0)
            summary_parts.append(f"  • {description} ({count}x)\n")
    else:
        summary_parts.append("\n⚠️  **Struggles:** None recorded. Great progress!\n")

    # Behavioural patterns
    if memory.behaviour_patterns:
        summary_parts.append("\n🔍 **Detected Patterns:**\n")
        for pattern_name, pattern_data in memory.behaviour_patterns.items():
            pattern_label = pattern_name.replace("_", " ").title()
            occurrences = pattern_data.get("occurrences", 0)
            summary_parts.append(f"  • {pattern_label} ({occurrences}x)\n")
    else:
        summary_parts.append("\n🔍 **Patterns:** No recurring patterns detected yet.\n")

    # Encouraging closing message
    summary_parts.append("\n" + "=" * 50 + "\n")
    summary_parts.append("\n💬 **Coach's Note:**\n")

    # Personalize based on streaks
    if memory.streaks and any(s.get("current", 0) > 0 for s in memory.streaks.values()):
        summary_parts.append(
            "You're making progress! Every day you maintain a streak,\n"
            "you're rewiring your habits. Keep it up! 🌟\n"
        )
    elif memory.struggles:
        summary_parts.append(
            "Remember: setbacks are part of the journey. Each struggle\n"
            "teaches you something. Focus on small wins! 💪\n"
        )
    else:
        summary_parts.append(
            "You're just getting started! Building better money habits\n"
            "takes time, but you've taken the first step. Stay consistent! 🚀\n"
        )

    return "".join(summary_parts)


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
    # Set up logging
    setup_logging()
    
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
