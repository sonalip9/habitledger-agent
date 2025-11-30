"""
Core agent logic & interaction flow.

This module contains the main HabitLedger coach agent that orchestrates
user interactions, coordinates behaviour analysis, and generates coaching responses.
It serves as the central controller that ties together memory management,
behaviour analysis, and response generation.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

from google.genai import Client
from google.genai.types import Content, GenerateContentConfig, Part

from src.adk_config import INSTRUCTION_TEXT
from src.adk_tools import behaviour_db_tool, get_behaviour_db_tool
from src.behaviour_engine import analyse_behaviour, explain_principle, load_behaviour_db
from src.config import setup_logging
from src.memory import MAX_CONVERSATION_CONTEXT_LENGTH, UserMemory
from src.memory_service import MemoryService
from src.models import AnalysisResult, BehaviourDatabase

from .config import get_adk_model_name, get_api_key, load_env

logger = logging.getLogger(__name__)


def _handle_low_confidence_case(
    principle_id: str,
    user_input: str,
    confidence: float,
    behaviour_db: dict[str, Any],
) -> str:
    """
    Handle low-confidence detections by asking clarifying questions.

    Args:
        principle_id: The tentatively detected principle ID.
        user_input: The user's original input.
        confidence: Confidence score for the detection.
        behaviour_db: Dictionary containing behavioural principles.

    Returns:
        str: Response with clarifying questions.
    """
    logger.info(
        "Low confidence detection (%.2f), asking clarifying questions",
        confidence,
        extra={
            "event": "low_confidence_handling",
            "principle_id": principle_id,
            "confidence": confidence,
        },
    )
    return _generate_clarifying_questions(principle_id, user_input, behaviour_db)


def _build_template_response(
    analysis: AnalysisResult,
    behaviour_db: dict[str, Any],
) -> str:
    """
    Build a template-based response from analysis results.

    Args:
        analysis: The behaviour analysis result.
        behaviour_db: Dictionary containing behavioural principles.

    Returns:
        str: Formatted template response with principle and interventions.
    """
    detected_principle_id = analysis.detected_principle_id
    reason = analysis.reason
    interventions = analysis.intervention_suggestions
    confidence = analysis.confidence
    behaviour_db_obj = BehaviourDatabase.from_dict(behaviour_db)

    response_parts = []

    if detected_principle_id:
        principle = behaviour_db_obj.get_principle_by_id(detected_principle_id)
        principle_name = principle.name if principle else detected_principle_id

        response_parts.append(f"🎯 **Detected Principle:** {principle_name}")
        if confidence < 0.8:
            response_parts.append(f" (Confidence: {int(confidence * 100)}%)")
        response_parts.append("\n")
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

    return "".join(response_parts)


def _finalize_response(
    response: str,
    analysis: AnalysisResult,
    memory: UserMemory,
    source: str,
) -> str:
    """
    Finalize response by recording it in memory.

    Args:
        response: The generated response text.
        analysis: The behaviour analysis result.
        memory: UserMemory instance.
        source: Source of the response ("adk" or "template").

    Returns:
        str: The response (unchanged).
    """
    detected_principle_id = analysis.detected_principle_id
    confidence = analysis.confidence
    interventions = analysis.intervention_suggestions

    # Record assistant response in conversation history
    memory.add_conversation_turn(
        "assistant",
        response,
        {
            "principle_id": detected_principle_id,
            "confidence": confidence,
            "source": source,
        },
    )

    # Update memory if intervention was provided
    if detected_principle_id and interventions:
        memory.record_interaction(
            {
                "type": "intervention",
                "principle_id": detected_principle_id,
                "description": interventions[0],
            }
        )

    return response


def _generate_clarifying_questions(
    principle_id: str,
    _user_input: str,
    behaviour_db: dict[str, Any],
) -> str:
    """
    Generate clarifying questions when confidence is low.

    Args:
        principle_id: The tentatively detected principle ID.
        user_input: The user's original input (reserved for future use).
        behaviour_db: Dictionary containing behavioural principles.

    Returns:
        str: Response with clarifying questions to gather more context.
    """
    principles = behaviour_db.get("principles", [])
    principle_data = next(
        (p for p in principles if p.get("id") == principle_id),
        None,
    )

    principle_name = (
        principle_data.get("name", principle_id) if principle_data else principle_id
    )

    response_parts = []
    response_parts.append("🤔 **Let me understand better...**\n\n")
    response_parts.append(
        f"I'm thinking this might relate to **{principle_name}**, "
        "but I'd like to know more to give you the best guidance.\n\n"
    )
    response_parts.append("**Can you tell me more about:**\n")

    # Generate contextual questions based on principle
    questions = _get_clarifying_questions_for_principle(principle_id)
    for i, question in enumerate(questions, 1):
        response_parts.append(f"{i}. {question}\n")

    response_parts.append(
        "\n💡 The more details you share, the better I can support you!"
    )

    return "".join(response_parts)


def _get_clarifying_questions_for_principle(principle_id: str) -> list[str]:
    """
    Get relevant clarifying questions for a specific principle.

    Args:
        principle_id: The principle ID to generate questions for.

    Returns:
        list[str]: List of 2-3 clarifying questions.
    """
    questions_map = {
        "loss_aversion": [
            "Have you been tracking this habit? How long have you been working on it?",
            "What would it feel like to lose your progress?",
            "Is there a specific goal or milestone you're worried about missing?",
        ],
        "habit_loops": [
            "What usually triggers this behavior? (Time of day, emotion, situation)",
            "What do you get out of doing this? (Relief, comfort, excitement)",
            "When did you first notice this pattern?",
        ],
        "commitment_devices": [
            "Have you tried to change this before? What happened?",
            "Who in your life knows about this goal?",
            "What would make it harder for you to give up on this?",
        ],
        "temptation_bundling": [
            "What activities do you genuinely enjoy doing?",
            "What makes this goal feel like a chore?",
            "Is there something fun you could combine with this?",
        ],
        "friction_reduction": [
            "What specific steps are required to do this?",
            "Which part feels most complicated or time-consuming?",
            "If this were super easy, would you do it more often?",
        ],
        "friction_increase": [
            "How easy is it to do this impulsive action right now?",
            "What steps are involved from urge to action?",
            "Have you noticed specific times when it's hardest to resist?",
        ],
        "default_effect": [
            "Is this something you have to remember to do manually?",
            "Would you benefit from automating any part of this?",
            "What's your current default behavior in this situation?",
        ],
        "micro_habits": [
            "What's the smallest version of this goal you could imagine?",
            "Does the goal feel overwhelming right now?",
            "What's one tiny thing you could do today?",
        ],
    }

    return questions_map.get(
        principle_id,
        [
            "What's the main challenge you're facing?",
            "When does this usually happen?",
            "What have you tried before?",
        ],
    )


def _build_adk_context(prompt_context: dict[str, Any]) -> str:
    """
    Build the context prompt for ADK agent.

    Args:
        prompt_context: Dictionary with user_input, analysis_result, memory_summary.

    Returns:
        str: Formatted context prompt.
    """
    user_input = prompt_context.get("user_input", "")
    analysis_result = prompt_context.get("analysis_result", {})
    memory_summary = prompt_context.get("memory_summary", "")

    principle_id = analysis_result.get("detected_principle_id")
    source = analysis_result.get("source", "unknown")

    return f"""User message: "{user_input}"

Context:
- Pre-analyzed principle: {principle_id or "None detected"}
- Detection source: {source}
- Memory: {memory_summary}

Generate a supportive, actionable coaching response. Use the behaviour_db_tool if you need more details about the detected principle or want to explore alternative principles."""


def _execute_adk_call(
    client: Any,
    model_name: str,
    context_prompt: str,
    config: Any,
) -> Any:
    """
    Execute the ADK agent call.

    Args:
        client: GenAI client.
        model_name: Model name to use.
        context_prompt: Context prompt string.
        config: Generation config.

    Returns:
        Response object from the model.
    """
    return client.models.generate_content(
        model=model_name,
        contents=context_prompt,
        config=config,
    )


def _handle_tool_response(
    client: Any,
    model_name: str,
    context_prompt: str,
    initial_response: Any,
    config: Any,
    user_input: str,
) -> Optional[str]:
    """
    Handle tool calls in ADK agent response.

    Args:
        client: GenAI client.
        model_name: Model name.
        context_prompt: Original context prompt.
        initial_response: Initial response from model.
        config: Generation config.
        user_input: Original user input.

    Returns:
        str or None: Final response text or None if no response.
    """

    final_response_parts = []

    if (
        initial_response.candidates
        and initial_response.candidates[0].content
        and initial_response.candidates[0].content.parts
    ):
        for part in initial_response.candidates[0].content.parts:
            if hasattr(part, "function_call") and part.function_call:
                # Execute the tool
                func_name = part.function_call.name
                args = part.function_call.args if part.function_call.args else {}

                if func_name == "behaviour_db_tool":
                    tool_input = (
                        args.get("user_input", user_input)
                        if hasattr(args, "get")
                        else user_input
                    )
                    tool_result = behaviour_db_tool(tool_input)

                    logger.info(
                        "ADK agent called tool",
                        extra={
                            "event": "tool_call",
                            "tool_name": func_name,
                            "principle_id": tool_result.get("detected_principle_id"),
                            "source": "adk",
                        },
                    )

                    # Send tool result back to agent for final response
                    tool_response_content = Content(
                        parts=[
                            Part.from_function_response(
                                name=func_name,
                                response=tool_result,
                            )
                        ]
                    )

                    # Continue conversation with tool result
                    final_response = client.models.generate_content(
                        model=model_name,
                        contents=[
                            context_prompt,
                            initial_response.candidates[0].content,
                            tool_response_content,
                        ],
                        config=config,
                    )

                    if (
                        final_response.candidates
                        and final_response.candidates[0].content
                        and final_response.candidates[0].content.parts
                    ):
                        for final_part in final_response.candidates[0].content.parts:
                            if hasattr(final_part, "text") and final_part.text:
                                final_response_parts.append(final_part.text)
            elif hasattr(part, "text") and part.text:
                final_response_parts.append(part.text)

    if final_response_parts:
        return "".join(final_response_parts)

    return None


def call_adk_agent(prompt_context: dict[str, Any]) -> Optional[str]:
    """
    Call the ADK agent to generate a natural-language coaching response.

    This function sends the user input and context (behaviour analysis, memory summary)
    to the ADK agent, which can use the behaviour_db_tool to retrieve interventions
    and generate a personalized coaching response.

    Args:
        prompt_context: Dictionary containing:
            - "user_input" (str): The user's original message
            - "analysis_result" (dict): Behaviour analysis result
            - "memory_summary" (str): Brief summary of user's memory/context

    Returns:
        str or None: The ADK agent's response text, or None if the call fails.

    Example:
        >>> context = {"user_input": "I keep ordering food", "analysis_result": {...}}
        >>> response = call_adk_agent(context)
        >>> if response:
        ...     print(response)
    """
    start_time = time.time()

    try:
        # Build context prompt
        context_prompt = _build_adk_context(prompt_context)
        user_input = prompt_context.get("user_input", "")

        # Initialize client
        api_key = get_api_key()
        client = Client(api_key=api_key)
        model_name = get_adk_model_name()

        config = GenerateContentConfig(
            system_instruction=INSTRUCTION_TEXT,
            tools=[get_behaviour_db_tool()],
            temperature=0.7,
        )

        # Execute ADK call
        response = _execute_adk_call(client, model_name, context_prompt, config)

        # Handle tool calls and get final response
        response_text = _handle_tool_response(
            client, model_name, context_prompt, response, config, user_input
        )

        if response_text:
            duration_ms = int((time.time() - start_time) * 1000)
            user_input_truncated = (
                user_input[:MAX_CONVERSATION_CONTEXT_LENGTH]
                if len(user_input) > MAX_CONVERSATION_CONTEXT_LENGTH
                else user_input
            )

            logger.info(
                "ADK agent response generated",
                extra={
                    "event": "response_generation",
                    "source": "adk",
                    "response_length": len(response_text),
                    "user_input": user_input_truncated,
                    "duration_ms": duration_ms,
                },
            )
            return response_text

        logger.warning("ADK agent returned no response")
        return None

    except Exception as e:  # noqa: BLE001
        duration_ms = int((time.time() - start_time) * 1000)
        logger.warning(
            "ADK agent call failed: %s",
            str(e),
            extra={
                "event": "response_generation",
                "source": "adk",
                "error": str(e),
                "duration_ms": duration_ms,
            },
            exc_info=True,
        )
        return None


def run_once(
    user_input: str,
    memory: UserMemory,
    behaviour_db: dict[str, Any],
) -> str:
    """
    Process a single user interaction and generate a coaching response.

    This function orchestrates the core agent loop for one interaction:
    1. Analyzes user input to detect relevant behavioural principles
    2. Attempts to generate response via ADK agent (with tool calling support)
    3. Falls back to template-based response if ADK fails
    4. Updates user memory with the interaction outcome

    Args:
        user_input: The user's message or description of their situation.
        memory: UserMemory instance to track user state across interactions.
        behaviour_db: Dictionary containing behavioural principles.

    Returns:
        str: A coaching response (ADK-generated or template-based) with principle
             detection and interventions, or general guidance if no principle detected.

    Example:
        >>> memory = UserMemory(user_id="user123")
        >>> db = load_behaviour_db("data/behaviour_principles.json")
        >>> response = run_once("I keep ordering food delivery", memory, db)
        >>> print(response)
        🎯 Detected Principle: Friction Increase (Make Bad Habits Hard)...
    """
    # Record user input in conversation history
    memory.add_conversation_turn("user", user_input)

    # Step 1: Analyze user behaviour
    analysis_dict = analyse_behaviour(user_input, memory, behaviour_db)
    analysis = AnalysisResult.from_dict(analysis_dict)

    # Step 2: Check confidence and handle low-confidence detections
    if analysis.confidence < 0.6 and analysis.detected_principle_id:
        response = _handle_low_confidence_case(
            analysis.detected_principle_id,
            user_input,
            analysis.confidence,
            behaviour_db,
        )
        memory.add_conversation_turn(
            "assistant",
            response,
            {"confidence": analysis.confidence, "clarification": True},
        )
        return response

    # Step 3: Build memory summary for context
    active_streaks = MemoryService.get_active_streaks(memory)
    recent_struggles = MemoryService.get_recent_struggles(memory)
    memory_summary = f"Goals: {len(memory.goals)}, Streaks: {len(active_streaks)}, Recent struggles: {len(recent_struggles)}"

    # Step 4: Try ADK agent for response generation
    prompt_context = {
        "user_input": user_input,
        "analysis_result": analysis_dict,
        "memory_summary": memory_summary,
    }

    adk_response = call_adk_agent(prompt_context)

    if adk_response:
        logger.info(
            "Using ADK agent response",
            extra={
                "event": "response_generation",
                "source": "adk",
                "principle_id": analysis.detected_principle_id,
                "confidence": analysis.confidence,
            },
        )
        return _finalize_response(adk_response, analysis, memory, "adk")

    # Step 5: Fallback to template-based response
    logger.info(
        "Falling back to template-based response",
        extra={
            "event": "response_generation",
            "source": "template",
            "principle_id": analysis.detected_principle_id,
            "confidence": analysis.confidence,
        },
    )

    template_response = _build_template_response(analysis, behaviour_db)
    return _finalize_response(template_response, analysis, memory, "template")


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
            current = streak_data.current
            best = streak_data.best
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
            key=lambda s: s.count,
            reverse=True,
        )[:3]

        for struggle in sorted_struggles:
            description = struggle.description
            count = struggle.count
            summary_parts.append(f"  • {description} ({count}x)\n")
    else:
        summary_parts.append("\n⚠️  **Struggles:** None recorded. Great progress!\n")

    # Behavioural patterns
    if memory.behaviour_patterns:
        summary_parts.append("\n🔍 **Detected Patterns:**\n")
        for pattern_name, pattern_data in memory.behaviour_patterns.items():
            pattern_label = pattern_name.replace("_", " ").title()
            occurrences = pattern_data.occurrences
            summary_parts.append(f"  • {pattern_label} ({occurrences}x)\n")
    else:
        summary_parts.append("\n🔍 **Patterns:** No recurring patterns detected yet.\n")

    # Encouraging closing message
    summary_parts.append("\n" + "=" * 50 + "\n")
    summary_parts.append("\n💬 **Coach's Note:**\n")

    # Personalize based on streaks
    if memory.streaks and any(s.current > 0 for s in memory.streaks.values()):
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
    # Load environment variables first
    load_env()

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
