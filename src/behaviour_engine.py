"""
Behaviour classification and interventions.

This module contains behaviour analysis and intervention selection logic for HabitLedger.
It analyzes user input to identify relevant behavioural science principles and suggests
appropriate interventions based on the detected patterns.

The module uses LLM-based analysis as the primary method, with deterministic,
keyword-based heuristics as a fallback when LLM analysis is unavailable or fails.
"""

import json
import logging
from typing import Any

from .llm_client import analyse_behaviour_with_llm
from .memory import UserMemory

# Set up logging
logger = logging.getLogger(__name__)

# Define keyword mappings for each principle
KEYWORD_MAPPINGS = {
    "loss_aversion": [
        "regret",
        "lose",
        "lost",
        "missing out",
        "afraid",
        "fear",
        "worry",
        "worried",
        "broke my streak",
        "failed",
    ],
    "habit_loops": [
        "always",
        "every time",
        "whenever",
        "habit",
        "routine",
        "automatic",
        "without thinking",
        "trigger",
        "stress",
        "bored",
        "evening",
    ],
    "commitment_devices": [
        "hard to stick",
        "need help",
        "accountability",
        "keep forgetting",
        "difficult to maintain",
        "tempted",
        "temptation",
        "willpower",
    ],
    "temptation_bundling": [
        "boring",
        "unmotivated",
        "don't enjoy",
        "tedious",
        "dread",
        "reward",
        "treat myself",
    ],
    "friction_reduction": [
        "complicated",
        "too many steps",
        "confusing",
        "difficult to",
        "hard to track",
        "time consuming",
        "inconvenient",
    ],
    "friction_increase": [
        "too easy",
        "one click",
        "instant",
        "impuls",
        "delivery",
        "shopping app",
        "online shopping",
        "food delivery",
        "quick purchase",
    ],
    "default_effect": [
        "forget to",
        "need to automate",
        "manual",
        "remember to",
        "set up automatic",
    ],
    "micro_habits": [
        "overwhelmed",
        "too much",
        "big goal",
        "don't know where to start",
        "small step",
        "just starting",
    ],
}


def analyse_behaviour(
    user_input: str,
    user_memory: UserMemory,
    behaviour_db: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyze user input to detect relevant behavioural principles and suggest interventions.

    This function first attempts to use LLM-based analysis for more nuanced understanding.
    If LLM analysis fails or is unavailable, it falls back to keyword-based heuristics
    to match user input against behavioural principles from the knowledge base.

    Args:
        user_input: The user's message or description of their behaviour/struggle.
        user_memory: UserMemory instance containing user's goals, streaks, and history.
        behaviour_db: Dictionary containing behavioural principles (from behaviour_principles.json).

    Returns:
        dict: Analysis result with the following keys:
            - "detected_principle_id" (str or None): ID of the matched principle
            - "reason" (str): Brief explanation of why this principle was selected
            - "intervention_suggestions" (list[str]): List of suggested interventions
            - "triggers_matched" (list[str]): List of triggers that matched the input
            - "source" (str): "adk" or "keyword" indicating classification method
            - "confidence" (float): Confidence score (0.0-1.0) for the detection

    Example:
        >>> from memory import UserMemory
        >>> memory = UserMemory(user_id="user123")
        >>> behaviour_db = {"principles": [...]}
        >>> result = analyse_behaviour("I keep ordering food delivery", memory, behaviour_db)
        >>> print(result["detected_principle_id"])
        friction_increase
    """
    # Try LLM-based analysis first
    logger.info("Attempting LLM-based behaviour analysis")
    llm_result = analyse_behaviour_with_llm(user_input, user_memory, behaviour_db)

    if llm_result:
        logger.info(
            "LLM analysis successful: %s",
            llm_result["detected_principle_id"],
        )
        # Apply adaptive weighting based on historical effectiveness
        llm_result = _apply_adaptive_weighting(llm_result, user_memory)
        return llm_result

    # Fall back to keyword-based analysis
    logger.info("LLM analysis failed or unavailable, using keyword-based fallback")
    keyword_result = _analyse_behaviour_keyword(user_input, user_memory, behaviour_db)
    # Apply adaptive weighting to keyword result as well
    return _apply_adaptive_weighting(keyword_result, user_memory)


def _analyse_behaviour_keyword(
    user_input: str,
    user_memory: UserMemory,
    behaviour_db: dict[str, Any],
) -> dict[str, Any]:
    """
    Analyze user input using keyword-based heuristics (fallback method).

    This is the original keyword-based analysis logic, now used as a fallback
    when LLM analysis is unavailable or fails.

    Args:
        user_input: The user's message or description of their behaviour/struggle.
        user_memory: UserMemory instance containing user's goals, streaks, and history.
        behaviour_db: Dictionary containing behavioural principles (from behaviour_principles.json).

    Returns:
        dict: Analysis result with the same structure as analyse_behaviour.
    """
    user_input_lower = user_input.lower()
    principles = behaviour_db.get("principles", [])

    # Score each principle based on keyword matches
    principle_scores: dict[str, int] = {}
    matched_keywords: dict[str, list[str]] = {}

    for principle_id, keywords in KEYWORD_MAPPINGS.items():
        score = 0
        matches = []
        for keyword in keywords:
            if keyword in user_input_lower:
                score += 1
                matches.append(keyword)

        if score > 0:
            principle_scores[principle_id] = score
            matched_keywords[principle_id] = matches

    # Also check user memory for additional context
    # If user has streaks, loss_aversion might be relevant
    if user_memory.streaks:
        principle_scores["loss_aversion"] = principle_scores.get("loss_aversion", 0) + 1

    # If user has many struggles, commitment_devices might help
    if len(user_memory.struggles) >= 2:
        principle_scores["commitment_devices"] = (
            principle_scores.get("commitment_devices", 0) + 1
        )

    # Select the principle with highest score
    if not principle_scores:
        # No clear match, return generic response
        logger.info(
            "No principle detected",
            extra={"principle_id": None, "source": "keyword"},
        )
        return {
            "detected_principle_id": None,
            "reason": "No specific behavioural pattern detected. General guidance provided.",
            "intervention_suggestions": [
                "Start by identifying specific triggers for your spending habits",
                "Track your expenses for a week to spot patterns",
                "Set one small, specific goal to work on",
            ],
            "triggers_matched": [],
            "source": "keyword",
            "confidence": 0.3,  # Low confidence for generic response
        }

    # Get the best matching principle
    best_principle_id = max(principle_scores, key=principle_scores.get)  # type: ignore
    matched_triggers = matched_keywords.get(best_principle_id, [])

    # Calculate confidence score
    total_keywords_for_principle = len(KEYWORD_MAPPINGS.get(best_principle_id, []))
    matched_count = len(matched_triggers)
    memory_bonus = 0
    if best_principle_id == "loss_aversion" and user_memory.streaks:
        memory_bonus += 1
    if best_principle_id == "commitment_devices" and len(user_memory.struggles) >= 2:
        memory_bonus += 1

    confidence = _calculate_confidence_score(
        matched_count,
        total_keywords_for_principle,
        memory_bonus,
    )

    # Find the full principle data
    principle_data = next(
        (p for p in principles if p.get("id") == best_principle_id), None
    )

    if not principle_data:
        logger.info(
            "Keyword classification - principle not in DB",
            extra={"principle_id": best_principle_id, "source": "keyword"},
        )
        # Recalculate confidence without memory bonus since principle not in DB
        confidence = _calculate_confidence_score(
            matched_count, total_keywords_for_principle, 0
        )

        return {
            "detected_principle_id": best_principle_id,
            "reason": f"Matched keywords: {', '.join(matched_triggers)}",
            "intervention_suggestions": [
                "Focus on building consistent habits",
                "Try small, incremental changes",
            ],
            "triggers_matched": matched_triggers,
            "source": "keyword",
            "confidence": confidence,
        }

    # Extract interventions from the principle
    interventions = principle_data.get("interventions", [])

    # Build reason based on matched triggers and principle
    reason = _build_reason(
        principle_data.get("name", ""),
        matched_triggers,
    )

    logger.info(
        "Keyword classification successful",
        extra={
            "principle_id": best_principle_id,
            "source": "keyword",
            "confidence": confidence,
        },
    )

    return {
        "detected_principle_id": best_principle_id,
        "reason": reason,
        "intervention_suggestions": interventions[:5],  # Return top 5 interventions
        "triggers_matched": matched_triggers,
        "source": "keyword",
        "confidence": confidence,
    }


def _apply_adaptive_weighting(
    result: dict[str, Any],
    user_memory: UserMemory,
) -> dict[str, Any]:
    """
    Apply adaptive weighting based on historical intervention effectiveness.

    This function adjusts confidence scores based on how well each principle
    has worked for this user in the past. Principles with higher success rates
    get boosted confidence when detected.

    Note: Adaptive weighting requires at least 2 historical uses of a principle
    before confidence adjustment is applied. This threshold ensures sufficient
    data to make meaningful adjustments based on success patterns.

    Args:
        result: Initial analysis result with detected principle.
        user_memory: UserMemory instance with intervention feedback.

    Returns:
        dict: Updated result with adjusted confidence score.
    """
    principle_id = result.get("detected_principle_id")
    base_confidence = result.get("confidence", 0.7)  # Default if not set

    if not principle_id or principle_id not in user_memory.intervention_feedback:
        # No historical data, return original confidence
        result["confidence"] = base_confidence
        return result

    # Get historical success rate for this principle
    feedback = user_memory.intervention_feedback[principle_id]
    success_rate = feedback.success_rate
    total_uses = feedback.total

    # Only adjust if we have enough data (at least 2 uses)
    # Single interventions don't provide sufficient signal for adaptation
    if total_uses < 2:
        result["confidence"] = base_confidence
        return result

    # Adjust confidence based on success rate
    # Success rate ranges from 0.0 to 1.0
    # We'll adjust confidence by ±20% based on success rate
    adjustment = (success_rate - 0.5) * 0.4  # Range: -0.2 to +0.2
    adjusted_confidence = min(1.0, max(0.1, base_confidence + adjustment))

    result["confidence"] = round(adjusted_confidence, 2)
    result["adjusted_by_history"] = True

    logger.info(
        "Applied adaptive weighting: %s (%.2f -> %.2f based on %.1f%% success)",
        principle_id,
        base_confidence,
        adjusted_confidence,
        success_rate * 100,
    )

    return result


def _calculate_confidence_score(
    matched_keywords_count: int,
    total_keywords: int,
    memory_context_bonus: int = 0,
) -> float:
    """
    Calculate confidence score for keyword-based detection.

    Args:
        matched_keywords_count: Number of keywords matched.
        total_keywords: Total keywords available for the principle.
        memory_context_bonus: Bonus points from memory context (0-2).

    Returns:
        float: Confidence score between 0.0 and 1.0.
    """
    # Base confidence from keyword matching
    if total_keywords == 0:
        keyword_confidence = 0.0
    else:
        keyword_confidence = min(matched_keywords_count / total_keywords, 1.0)

    # Apply memory context bonus (max +0.2)
    memory_bonus = min(memory_context_bonus * 0.1, 0.2)

    # Combine and cap at 1.0
    confidence = min(keyword_confidence * 0.8 + memory_bonus, 1.0)

    # Keyword-based detection is inherently less confident than LLM
    # So we cap it at 0.75 for keyword matches
    confidence = min(confidence, 0.75)

    return round(confidence, 2)


def _build_reason(
    principle_name: str,
    matched_triggers: list[str],
) -> str:
    """
    Build a human-readable explanation for why a principle was selected.

    Args:
        principle_name: Name of the selected behavioural principle.
        matched_triggers: List of keywords that matched in user input.

    Returns:
        str: Clear explanation of the match.

    Example:
        >>> reason = _build_reason("Loss Aversion", ["regret", "failed"])
        >>> print(reason)
        Detected Loss Aversion based on your mention of regret, failed...
    """
    if not matched_triggers:
        return f"Your situation relates to {principle_name}."

    trigger_text = ", ".join(matched_triggers[:3])  # Show up to 3 triggers

    if len(matched_triggers) > 3:
        trigger_text += f" (and {len(matched_triggers) - 3} more)"

    return f"Detected {principle_name} based on your mention of {trigger_text}. This principle can help you address the pattern you described."


def get_interventions(principle_id: str, behaviour_db: dict[str, Any]) -> list[str]:
    """
    Get intervention suggestions for a specific behavioural principle.

    This function looks up a principle by ID in the behaviour database
    and returns a subset of its intervention strategies.

    Args:
        principle_id: The ID of the behavioural principle (e.g., "loss_aversion").
        behaviour_db: Dictionary containing behavioural principles from behaviour_principles.json.

    Returns:
        list[str]: A list of 1-2 intervention suggestions for the principle,
                   or an empty list if principle not found.

    Example:
        >>> db = {"principles": [{"id": "friction_increase", "interventions": ["Delete apps", "Remove cards"]}]}
        >>> interventions = get_interventions("friction_increase", db)
        >>> print(len(interventions))
        2
    """
    principles = behaviour_db.get("principles", [])

    # Find the matching principle
    principle_data = next(
        (p for p in principles if p.get("id") == principle_id),
        None,
    )

    if not principle_data:
        return []

    # Return top 1-2 interventions
    all_interventions = principle_data.get("interventions", [])
    return all_interventions[:2]


def explain_principle(principle_id: str, behaviour_db: dict[str, Any]) -> str:
    """
    Generate a behavioural explanation for a detected principle.

    This function retrieves the name and description of a behavioural principle
    from the knowledge base and formats it as a clear, educational explanation
    to help users understand the "why" behind suggested interventions.

    Args:
        principle_id: The ID of the behavioural principle (e.g., "loss_aversion").
        behaviour_db: Dictionary containing behavioural principles from behaviour_principles.json.

    Returns:
        str: A formatted explanation of the principle including its name and description,
             or a generic message if the principle is not found.

    Example:
        >>> db = {"principles": [{"id": "loss_aversion", "name": "Loss Aversion", "description": "We feel losses more..."}]}
        >>> explanation = explain_principle("loss_aversion", db)
        >>> print(explanation)
        This suggestion is based on the principle of Loss Aversion — We feel losses more...
    """
    principles = behaviour_db.get("principles", [])

    # Find the matching principle
    principle_data = next(
        (p for p in principles if p.get("id") == principle_id),
        None,
    )

    if not principle_data:
        return "This suggestion is based on behavioural science research to help you build better habits."

    principle_name = principle_data.get("name", principle_id)
    principle_description = principle_data.get(
        "description", "This principle helps explain patterns in financial behaviour."
    )

    return f"**Why this works:** This suggestion is based on the principle of **{principle_name}** — {principle_description}"


def load_behaviour_db(db_path: str) -> dict[str, Any]:
    """
    Load the behaviour principles database from a JSON file.

    Args:
        db_path: Path to the behaviour_principles.json file.

    Returns:
        dict: The loaded behaviour database.

    Raises:
        FileNotFoundError: If the database file doesn't exist.
        json.JSONDecodeError: If the file contains invalid JSON.

    Example:
        >>> db = load_behaviour_db("data/behaviour_principles.json")
        >>> print(len(db["principles"]))
        8
    """
    from pathlib import Path

    file_path = Path(db_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Behaviour database not found: {db_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
