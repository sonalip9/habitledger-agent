"""
LLM client for behaviour analysis using Google ADK.

This module provides LLM-based behaviour analysis functionality for HabitLedger.
It uses the Google GenAI API to analyze user input and recommend appropriate
behavioural principles and interventions.
"""

import logging
import time
from typing import Any

from google.genai import Client
from google.genai.types import (
    FunctionDeclaration,
    GenerateContentConfig,
    Schema,
    Tool,
    Type,
)

from .config import get_adk_model_name, get_api_key

# Set up logging
logger = logging.getLogger(__name__)


def _build_llm_prompt(
    user_input: str,
    user_memory: Any,
) -> str:
    """
    Build the prompt for LLM behaviour analysis.

    Args:
        user_input: The user's message.
        user_memory: UserMemory instance.

    Returns:
        str: Formatted prompt for the LLM.
    """
    # Build context from user memory
    memory_context = _build_memory_context(user_memory)

    # Include recent conversation context
    conversation_context = ""
    if hasattr(user_memory, "build_conversation_context"):
        conversation_context = user_memory.build_conversation_context(num_turns=5)

    # Include user profile for personalization
    profile_context = ""
    if hasattr(user_memory, "user_profile") and user_memory.user_profile:
        profile = user_memory.user_profile
        profile_context = f"""User Profile:
- Preferred tone: {profile.preferred_tone}
- Engagement level: {profile.engagement_level}
- Learning pace: {profile.learning_speed}"""

    return f"""Analyze the following user situation and identify the most relevant behavioural science principle.

User Input: {user_input}

User Context:
{memory_context}

{conversation_context}

{profile_context}

Please analyze this situation and use the analyse_behaviour tool to provide:
1. The most relevant behavioural principle ID
2. Clear reasoning for your selection
3. 1-3 specific, actionable intervention suggestions
4. The key triggers or phrases that led to your selection"""


def _parse_llm_response(
    response: Any,
    behaviour_db: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Parse the LLM response and extract analysis results.

    Args:
        response: The LLM response object.
        behaviour_db: Dictionary containing behavioural principles.

    Returns:
        dict or None: Analysis result if successful, None otherwise.
    """
    if (
        response.candidates
        and response.candidates[0].content
        and response.candidates[0].content.parts
    ):
        for part in response.candidates[0].content.parts:
            if hasattr(part, "function_call") and part.function_call:
                # Extract the function call arguments
                args = part.function_call.args

                # Convert to our expected format
                result = {
                    "detected_principle_id": args.get("principle_id"),
                    "reason": args.get("reason", ""),
                    "intervention_suggestions": list(
                        args.get("intervention_suggestions", [])
                    ),
                    "triggers_matched": list(args.get("triggers_matched", [])),
                    "source": "adk",
                    "confidence": 0.85,  # LLM-based detection has higher base confidence
                }

                return _validate_principle(result, behaviour_db)

    return None


def _validate_principle(
    result: dict[str, Any],
    behaviour_db: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Validate that the detected principle exists and populate interventions if needed.

    Args:
        result: The analysis result to validate.
        behaviour_db: Dictionary containing behavioural principles.

    Returns:
        dict or None: Validated result or None if invalid.
    """
    principles = behaviour_db.get("principles", [])

    # Validate the principle exists in the database
    if not any(p.get("id") == result["detected_principle_id"] for p in principles):
        logger.warning(
            "LLM suggested unknown principle: %s",
            result["detected_principle_id"],
        )
        return None

    # If interventions are empty, get them from the database
    if not result["intervention_suggestions"]:
        principle_data = next(
            (p for p in principles if p.get("id") == result["detected_principle_id"]),
            None,
        )
        if principle_data:
            result["intervention_suggestions"] = principle_data.get(
                "interventions", []
            )[:3]

    return result


def _create_behaviour_analysis_tool(behaviour_db: dict[str, Any]) -> Tool:
    """
    Create a tool definition for the LLM to use for behaviour analysis.

    This tool provides the LLM with information about available behavioural
    principles and asks it to recommend which principle(s) match the user's
    situation.

    Args:
        behaviour_db: Dictionary containing behavioural principles from behaviour_principles.json.

    Returns:
        Tool: Configured tool with behaviour analysis function declaration.
    """
    # Extract principle information for the tool description
    principles = behaviour_db.get("principles", [])
    principle_descriptions = []

    for principle in principles:
        principle_id = principle.get("id", "")
        name = principle.get("name", "")
        description = principle.get("description", "")
        principle_descriptions.append(f"- {principle_id}: {name} - {description}")

    principles_list = "\n".join(principle_descriptions)

    # Create schema for parameters
    parameters_schema = Schema(
        type=Type.OBJECT,
        properties={
            "principle_id": Schema(
                type=Type.STRING,
                description=(
                    f"The ID of the most relevant behavioural principle. "
                    f"Available principles:\n{principles_list}"
                ),
            ),
            "reason": Schema(
                type=Type.STRING,
                description="Clear explanation of why this principle was selected based on the user's input",
            ),
            "intervention_suggestions": Schema(
                type=Type.ARRAY,
                items=Schema(type=Type.STRING),
                description="List of 1-3 specific, actionable intervention suggestions for the user",
            ),
            "triggers_matched": Schema(
                type=Type.ARRAY,
                items=Schema(type=Type.STRING),
                description="List of specific words or phrases from user input that indicated this principle",
            ),
        },
        required=[
            "principle_id",
            "reason",
            "intervention_suggestions",
            "triggers_matched",
        ],
    )

    function_declaration = FunctionDeclaration(
        name="analyse_behaviour",
        description=(
            "Analyzes user's financial habit situation and identifies the most relevant "
            "behavioural science principle. Returns the principle ID, reasoning, "
            "intervention suggestions, and matched triggers."
        ),
        parameters=parameters_schema,
    )

    return Tool(function_declarations=[function_declaration])


def analyse_behaviour_with_llm(
    user_input: str,
    user_memory: Any,
    behaviour_db: dict[str, Any],
) -> dict[str, Any] | None:
    """
    Analyze user input using LLM to detect relevant behavioural principles.

    This function uses the Google GenAI API to analyze user input and recommend
    appropriate behavioural principles and interventions. It leverages the LLM's
    understanding of context and nuance to make better recommendations than
    keyword-based matching alone.

    Args:
        user_input: The user's message or description of their behaviour/struggle.
        user_memory: UserMemory instance containing user's goals, streaks, and history.
        behaviour_db: Dictionary containing behavioural principles (from behaviour_principles.json).

    Returns:
        dict or None: Analysis result with the following keys if successful:
            - "detected_principle_id" (str): ID of the matched principle
            - "reason" (str): Brief explanation of why this principle was selected
            - "intervention_suggestions" (list[str]): List of suggested interventions
            - "triggers_matched" (list[str]): List of triggers that matched the input
            - "confidence" (float): Confidence score (0.0-1.0) for the detection
            - "source" (str): "adk" indicating LLM-based detection
        Returns None if LLM analysis fails.

    Example:
        >>> from memory import UserMemory
        >>> memory = UserMemory(user_id="user123")
        >>> behaviour_db = {"principles": [...]}
        >>> result = analyse_behaviour_with_llm("I keep ordering food delivery", memory, behaviour_db)
        >>> print(result["detected_principle_id"]) if result else print("Failed")
        friction_increase
    """

    start_time = time.time()
    user_input_truncated = user_input[:100] if len(user_input) > 100 else user_input

    logger.info(
        "Starting LLM behaviour analysis",
        extra={
            "event": "llm_analysis_start",
            "user_input_preview": user_input_truncated,
            "memory_goals_count": (
                len(user_memory.goals) if hasattr(user_memory, "goals") else 0
            ),
            "memory_streaks_count": (
                len(user_memory.streaks) if hasattr(user_memory, "streaks") else 0
            ),
        },
    )

    try:
        # Initialize client
        api_key = get_api_key()
        client = Client(api_key=api_key)
        model_name = get_adk_model_name()

        logger.debug(
            "LLM client initialized",
            extra={"model": model_name},
        )

        # Create the behaviour analysis tool
        analysis_tool = _create_behaviour_analysis_tool(behaviour_db)

        # Build prompt
        prompt = _build_llm_prompt(user_input, user_memory)

        # Configure the generation
        config = GenerateContentConfig(
            tools=[analysis_tool],
            temperature=0.3,  # Lower temperature for more consistent analysis
        )

        # Generate response
        logger.info(
            "Sending request to LLM for behaviour analysis",
            extra={"model": model_name, "temperature": config.temperature},
        )

        llm_start = time.time()
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config,
        )
        llm_duration_ms = int((time.time() - llm_start) * 1000)

        logger.info(
            "LLM response received",
            extra={
                "event": "llm_response",
                "duration_ms": llm_duration_ms,
                "has_candidates": bool(response.candidates),
            },
        )

        # Parse and validate response
        result = _parse_llm_response(response, behaviour_db)

        if result:
            total_duration_ms = int((time.time() - start_time) * 1000)
            logger.info(
                "LLM analysis successful",
                extra={
                    "event": "llm_analysis_complete",
                    "principle_id": result.get("detected_principle_id", "unknown"),
                    "reason": result.get("reason", "N/A")[:150],
                    "intervention_count": len(
                        result.get("intervention_suggestions", [])
                    ),
                    "triggers_count": len(result.get("triggers_matched", [])),
                    "total_duration_ms": total_duration_ms,
                    "source": "adk",
                },
            )
            logger.debug(
                "LLM detailed results",
                extra={
                    "interventions": result.get("intervention_suggestions", []),
                    "triggers": result.get("triggers_matched", []),
                },
            )
            return result

        total_duration_ms = int((time.time() - start_time) * 1000)
        logger.warning(
            "LLM did not return a function call",
            extra={
                "event": "llm_analysis_failed",
                "reason": "no_function_call",
                "duration_ms": total_duration_ms,
            },
        )
        return None

    except Exception as e:  # noqa: BLE001
        total_duration_ms = int((time.time() - start_time) * 1000)
        logger.error(
            "LLM analysis failed: %s",
            str(e),
            extra={
                "event": "llm_analysis_error",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "duration_ms": total_duration_ms,
            },
            exc_info=True,
        )
        return None


def _build_memory_context(user_memory: Any) -> str:
    """
    Build a context string from user memory for the LLM.

    Args:
        user_memory: UserMemory instance containing user's goals, streaks, and history.

    Returns:
        str: Formatted context string summarizing user's state.
    """
    context_parts = []

    # Add goals
    if hasattr(user_memory, "goals") and user_memory.goals:
        goals_text = ", ".join(
            g.get("description", str(g)) if isinstance(g, dict) else str(g)
            for g in user_memory.goals
        )
        context_parts.append(f"Goals: {goals_text}")

    # Add streaks
    if hasattr(user_memory, "streaks") and user_memory.streaks:
        streak_count = len(user_memory.streaks)
        active_streaks = sum(
            1
            for s in user_memory.streaks.values()
            if isinstance(s, dict) and s.get("current", 0) > 0
        )
        context_parts.append(f"Streaks: {active_streaks}/{streak_count} active")

    # Add struggles
    if hasattr(user_memory, "struggles") and user_memory.struggles:
        struggle_count = len(user_memory.struggles)
        context_parts.append(f"Recorded struggles: {struggle_count}")

    return "\n".join(context_parts) if context_parts else "No prior context available"
