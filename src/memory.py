"""
Simple memory and persistence utilities.

This module manages user data persistence including goals, habit streaks,
and conversation history for the HabitLedger agent.

The UserMemory class provides a single-responsibility interface for storing
and retrieving user state without mixing in business logic or behaviour analysis.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .models import (
    ConversationRole,
    ConversationTurn,
    Goal,
    Intervention,
    InterventionFeedback,
    StreakData,
    Struggle,
)

# Module-level logger for consistent logging across all functions
logger = logging.getLogger(__name__)

# Maximum character length for truncating conversation content in context building
MAX_CONVERSATION_CONTEXT_LENGTH = 200


# TODO: Add test coverage for UserProfile class:
#   1. Default initialization with correct default values
#   2. to_dict() serialization produces correct structure
#   3. from_dict() deserialization handles missing fields with defaults
#   4. update_from_interaction() correctly updates engagement level and learning speed
#   5. State transitions (e.g., "low" → "medium" → "high" engagement)
class UserProfile:
    """
    Tracks user personality and preferences for adaptive response generation.

    This class learns about the user's motivation style, risk tolerance, and
    engagement patterns to enable personalized coaching responses.

    Attributes:
        motivation_style (str): User's primary motivation (e.g., "achievement", "fear_avoidance", "social").
        risk_tolerance (str): User's comfort with challenges ("low", "medium", "high").
        engagement_level (str): Current engagement pattern ("high", "medium", "low").
        preferred_tone (str): Communication preference ("direct", "supportive", "educational").
        learning_speed (str): How quickly user adopts suggestions ("fast", "moderate", "slow").
    """

    def __init__(
        self,
        motivation_style: str = "unknown",
        risk_tolerance: str = "medium",
        engagement_level: str = "medium",
        preferred_tone: str = "supportive",
        learning_speed: str = "moderate",
    ):
        self.motivation_style = motivation_style
        self.risk_tolerance = risk_tolerance
        self.engagement_level = engagement_level
        self.preferred_tone = preferred_tone
        self.learning_speed = learning_speed

    def to_dict(self) -> dict[str, Any]:
        """Serialize UserProfile to dictionary."""
        return {
            "motivation_style": self.motivation_style,
            "risk_tolerance": self.risk_tolerance,
            "engagement_level": self.engagement_level,
            "preferred_tone": self.preferred_tone,
            "learning_speed": self.learning_speed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserProfile":
        """Deserialize UserProfile from dictionary."""
        return cls(
            motivation_style=data.get("motivation_style", "unknown"),
            risk_tolerance=data.get("risk_tolerance", "medium"),
            engagement_level=data.get("engagement_level", "medium"),
            preferred_tone=data.get("preferred_tone", "supportive"),
            learning_speed=data.get("learning_speed", "moderate"),
        )

    def update_from_interaction(self, outcome: dict[str, Any]) -> None:
        """
        Update profile based on interaction outcomes.

        Args:
            outcome: Dictionary containing interaction feedback like success rate,
                    response_quality, engagement_indicators.
        """
        # Update engagement level based on interaction frequency
        if outcome.get("engaged", False):
            if self.engagement_level == "low":
                self.engagement_level = "medium"
            elif self.engagement_level == "medium":
                self.engagement_level = "high"

        # Update learning speed based on intervention success
        if outcome.get("intervention_successful", False):
            if self.learning_speed == "slow":
                self.learning_speed = "moderate"
            elif self.learning_speed == "moderate":
                self.learning_speed = "fast"


class UserMemory:
    """
    Manages persistent memory state for a single user.

    This class tracks user goals, habit streaks, struggles, and interaction history.
    It provides serialization/deserialization to/from JSON files for persistence.

    The class focuses solely on data storage and retrieval, avoiding business logic
    about habit analysis or intervention strategies (which belong in behaviour_engine.py).

    Attributes:
        user_id (str): Unique identifier for the user.
        goals (list[Goal]): List of user financial goals.
        streaks (dict[str, StreakData]): Dictionary tracking habit streaks (e.g., no_food_delivery).
        struggles (list[Struggle]): List of recorded user struggles with dates.
        interventions (list[Intervention]): History of suggested interventions.
        last_check_in (str): ISO format timestamp of last interaction.
        behaviour_patterns (dict): Detected patterns (e.g., end_of_month_overspending).
        conversation_history (list[ConversationTurn]): Multi-turn conversation log with role, content, timestamp.
        intervention_feedback (dict[str, InterventionFeedback]): Tracks effectiveness of each principle.
        user_profile (UserProfile): Personalization settings for adaptive responses.

    Example:
        >>> memory = UserMemory(user_id="user123")
        >>> memory.goals.append(Goal(description="Save ₹5000/month"))
        >>> memory.save_to_file("data/user123.json")
        >>> loaded = UserMemory.load_from_file("data/user123.json")
    """

    def __init__(
        self,
        user_id: str = "default_user",
        goals: Optional[list[Goal]] = None,
        streaks: Optional[dict[str, StreakData]] = None,
        struggles: Optional[list[Struggle]] = None,
        interventions: Optional[list[Intervention]] = None,
        last_check_in: Optional[str] = None,
        behaviour_patterns: Optional[dict] = None,
        conversation_history: Optional[list[ConversationTurn]] = None,
        intervention_feedback: Optional[dict[str, InterventionFeedback]] = None,
        user_profile: Optional[UserProfile] = None,
    ):
        """
        Initialize UserMemory with sensible defaults.

        Args:
            user_id: Unique identifier for the user (default: "default_user").
            goals: List of user goals (default: empty list).
            streaks: Dictionary of habit streaks (default: empty dict).
            struggles: List of recorded struggles (default: empty list).
            interventions: History of interventions (default: empty list).
            last_check_in: ISO timestamp of last check-in (default: current time).
            behaviour_patterns: Detected patterns (default: empty dict).
            conversation_history: Multi-turn conversation log (default: empty list).
            intervention_feedback: Effectiveness tracking per principle (default: empty dict).
            user_profile: Personalization settings (default: new UserProfile instance).
        """
        self.user_id = user_id
        self.goals = goals if goals is not None else []
        self.streaks = streaks if streaks is not None else {}
        self.struggles = struggles if struggles is not None else []
        self.interventions = interventions if interventions is not None else []
        self.last_check_in = last_check_in or datetime.now().isoformat()
        self.behaviour_patterns = (
            behaviour_patterns if behaviour_patterns is not None else {}
        )
        self.conversation_history = (
            conversation_history if conversation_history is not None else []
        )
        self.intervention_feedback = (
            intervention_feedback if intervention_feedback is not None else {}
        )
        self.user_profile = user_profile if user_profile is not None else UserProfile()

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize UserMemory to a dictionary.

        Returns:
            dict: Dictionary representation of the UserMemory instance.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> data = memory.to_dict()
            >>> print(data["user_id"])
            user123
        """
        return {
            "user_id": self.user_id,
            "goals": [g.to_dict() for g in self.goals],
            "streaks": {k: v.to_dict() for k, v in self.streaks.items()},
            "struggles": [s.to_dict() for s in self.struggles],
            "interventions": [i.to_dict() for i in self.interventions],
            "last_check_in": self.last_check_in,
            "behaviour_patterns": self.behaviour_patterns,
            "conversation_history": [t.to_dict() for t in self.conversation_history],
            "intervention_feedback": {
                k: v.to_dict() for k, v in self.intervention_feedback.items()
            },
            "user_profile": self.user_profile.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserMemory":
        """
        Deserialize UserMemory from a dictionary.

        Args:
            data: Dictionary containing UserMemory data.

        Returns:
            UserMemory: A new UserMemory instance populated with the data.

        Example:
            >>> data = {"user_id": "user123", "goals": [], "streaks": {}}
            >>> memory = UserMemory.from_dict(data)
            >>> print(memory.user_id)
            user123
        """
        profile_data = data.get("user_profile", {})
        user_profile = (
            UserProfile.from_dict(profile_data) if profile_data else UserProfile()
        )

        # Convert goals from dict to Goal objects
        goals_data = data.get("goals", [])
        goals = [Goal.from_dict(g) if isinstance(g, dict) else g for g in goals_data]

        # Convert streaks from dict to StreakData objects
        streaks_data = data.get("streaks", {})
        streaks = {
            k: StreakData.from_dict(v) if isinstance(v, dict) else v
            for k, v in streaks_data.items()
        }

        # Convert struggles from dict to Struggle objects
        struggles_data = data.get("struggles", [])
        struggles = [
            Struggle.from_dict(s) if isinstance(s, dict) else s for s in struggles_data
        ]

        # Convert interventions from dict to Intervention objects
        interventions_data = data.get("interventions", [])
        interventions = [
            Intervention.from_dict(i) if isinstance(i, dict) else i
            for i in interventions_data
        ]

        # Convert conversation history from dict to ConversationTurn objects
        conversation_data = data.get("conversation_history", [])
        conversation_history = [
            ConversationTurn.from_dict(t) if isinstance(t, dict) else t
            for t in conversation_data
        ]

        # Convert intervention feedback from dict to InterventionFeedback objects
        feedback_data = data.get("intervention_feedback", {})
        intervention_feedback = {
            k: InterventionFeedback.from_dict(v) if isinstance(v, dict) else v
            for k, v in feedback_data.items()
        }

        return cls(
            user_id=data.get("user_id", "default_user"),
            goals=goals,
            streaks=streaks,
            struggles=struggles,
            interventions=interventions,
            last_check_in=data.get("last_check_in"),
            behaviour_patterns=data.get("behaviour_patterns", {}),
            conversation_history=conversation_history,
            intervention_feedback=intervention_feedback,
            user_profile=user_profile,
        )

    @classmethod
    def load_from_file(cls, path: str) -> "UserMemory":
        """
        Load UserMemory from a JSON file.

        Args:
            path: Path to the JSON file containing user memory data.

        Returns:
            UserMemory: A UserMemory instance loaded from the file.

        Raises:
            FileNotFoundError: If the file does not exist.
            json.JSONDecodeError: If the file contains invalid JSON.

        Example:
            >>> memory = UserMemory.load_from_file("data/user123.json")
            >>> print(memory.user_id)
            user123
        """
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"Memory file not found: {path}")

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def save_to_file(self, path: str) -> None:
        """
        Save UserMemory to a JSON file.

        Creates parent directories if they don't exist.

        Args:
            path: Path where the JSON file should be saved.

        Raises:
            IOError: If the file cannot be written.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> memory.save_to_file("data/user123.json")
        """
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

        logger.info(
            "Memory saved to file",
            extra={
                "event": "memory_save",
                "user_id": self.user_id,
                "file_path": str(file_path),
                "goals_count": len(self.goals),
                "streaks_count": len(self.streaks),
                "interventions_count": len(self.interventions),
                "conversations_count": len(self.conversation_history),
            },
        )

    def save_to_session_state(
        self, session_state: dict[str, Any], key_prefix: str = "user:"
    ) -> None:
        """
        Save UserMemory to ADK session state with "user:" scoping.

        This helper function currently only implements the "user:" scope prefix
        for cross-session persistence. ADK supports three scoping prefixes:
        - 'user:' prefix: persists across all sessions for this user (implemented)
        - No prefix: session-scoped only (not implemented in this helper)
        - 'temp:' prefix: discarded after invocation (not implemented in this helper)

        TODO: Implement support for all three scoping levels (user:, temp:, no prefix).

        Args:
            session_state: The session.state dictionary to update.
            key_prefix: Prefix for state keys (default: "user:" for cross-session persistence).

        Example:
            >>> from google.adk.sessions import Session
            >>> session = Session(id='test', app_name='habitledger', userId='user123')
            >>> memory = UserMemory(user_id='user123')
            >>> memory.save_to_session_state(session.state)
            >>> print(session.state['user:memory'])
        """
        # Store full memory dict under single key for simplicity
        memory_key = f"{key_prefix}memory" if key_prefix else "memory"
        session_state[memory_key] = self.to_dict()

    @classmethod
    def load_from_session_state(
        cls,
        session_state: dict[str, Any],
        key_prefix: str = "user:",
    ) -> Optional["UserMemory"]:
        """
        Load UserMemory from ADK session state.

        Args:
            session_state: The session.state dictionary to read from.
            key_prefix: Prefix for state keys (default: "user:").

        Returns:
            UserMemory or None: Loaded memory if found, None otherwise.

        Example:
            >>> from google.adk.sessions import Session
            >>> session = Session(id='test', app_name='habitledger', userId='user123')
            >>> memory = UserMemory.load_from_session_state(session.state)
        """
        memory_key = f"{key_prefix}memory" if key_prefix else "memory"
        memory_dict = session_state.get(memory_key)

        if memory_dict:
            return cls.from_dict(memory_dict)
        return None

    def record_interaction(self, outcome: dict[str, Any]) -> None:
        """
        Record an interaction outcome to update streaks and struggles.

        This method updates the user's memory based on the outcome of an interaction.
        It can increment/reset streaks, add new struggles, or record interventions.

        Args:
            outcome: Dictionary containing interaction details. Expected keys:
                - "type": Type of outcome ("streak_update", "struggle", "intervention")
                - "streak_name": Name of streak to update (for streak_update)
                - "success": Boolean indicating if habit was maintained (for streak_update)
                - "description": Description of struggle or intervention
                - "principle_id": ID of behavioural principle applied (for intervention)

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> outcome = {
            ...     "type": "streak_update",
            ...     "streak_name": "no_food_delivery",
            ...     "success": True
            ... }
            >>> memory.record_interaction(outcome)
            >>> print(memory.streaks["no_food_delivery"]["current"])
            1
        """
        outcome_type = outcome.get("type")
        timestamp = datetime.now().isoformat()

        if outcome_type == "streak_update":
            streak_name = outcome.get("streak_name")
            success = outcome.get("success", False)

            if streak_name:
                if streak_name not in self.streaks:
                    self.streaks[streak_name] = StreakData(
                        current=0,
                        best=0,
                        last_updated=timestamp,
                    )

                streak = self.streaks[streak_name]
                if success:
                    streak.current += 1
                    if streak.current > streak.best:
                        streak.best = streak.current
                else:
                    streak.current = 0

                streak.last_updated = timestamp

        elif outcome_type == "struggle":
            description = outcome.get("description", "")
            if description:
                # Check if this struggle already exists
                existing = next(
                    (s for s in self.struggles if s.description == description),
                    None,
                )
                if existing:
                    existing.count = existing.count + 1
                    existing.last_noted = timestamp
                else:
                    self.struggles.append(
                        Struggle(
                            description=description,
                            first_noted=timestamp,
                            last_noted=timestamp,
                            count=1,
                        )
                    )

        elif outcome_type == "intervention":
            self.interventions.append(
                Intervention(
                    date=timestamp,
                    intervention_type=outcome.get("principle_id", "unknown"),
                    description=outcome.get("description", ""),
                )
            )

        # Update last check-in timestamp
        self.last_check_in = timestamp

        # Log the interaction recording using module-level logger
        logger.info(
            "Interaction recorded",
            extra={
                "event": "interaction_recorded",
                "user_id": self.user_id,
                "outcome_type": outcome_type,
                "streak_name": outcome.get("streak_name"),
                "principle_id": outcome.get("principle_id"),
                "timestamp": timestamp,
            },
        )

    def add_conversation_turn(
        self,
        role: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Add a conversation turn to the history.

        Args:
            role: The role of the speaker ("user", "assistant", "system").
            content: The message content.
            metadata: Optional metadata like principle_id, confidence, etc.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> memory.add_conversation_turn("user", "I keep ordering food delivery")
            >>> memory.add_conversation_turn("assistant", "Let's work on that...", {"principle_id": "friction_increase"})
        """
        timestamp = datetime.now().isoformat()

        # Convert role string to ConversationRole enum
        try:
            role_enum = ConversationRole(role)
        except ValueError:
            role_enum = ConversationRole.USER

        turn = ConversationTurn(
            role=role_enum,
            content=content,
            timestamp=timestamp,
            metadata=metadata or {},
        )

        self.conversation_history.append(turn)

        # Implement conversation windowing - keep last 50 turns
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

    def build_conversation_context(self, num_turns: int = 10) -> str:
        """
        Build a formatted context string from recent conversation history.

        Args:
            num_turns: Number of recent turns to include (default: 10).

        Returns:
            str: Formatted conversation context for LLM prompts.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> memory.add_conversation_turn("user", "I keep spending too much")
            >>> context = memory.build_conversation_context(num_turns=5)
        """
        if not self.conversation_history:
            return "No previous conversation."

        recent_turns = self.conversation_history[-num_turns:]
        context_parts = ["Recent conversation:"]

        for turn in recent_turns:
            role = turn.role.value.capitalize()
            content = turn.content[:MAX_CONVERSATION_CONTEXT_LENGTH]
            context_parts.append(f"{role}: {content}")

        return "\n".join(context_parts)

    def record_intervention_feedback(
        self,
        principle_id: str,
        success: bool,
    ) -> None:
        """
        Record the effectiveness of an intervention based on a principle.

        TODO: Add test coverage for this method. Tests should verify:
        1. Creating new feedback entry for a principle
        2. Incrementing success/failure counts correctly
        3. Calculating success_rate accurately (successes / total)
        4. Multiple feedback recordings accumulate correctly

        This enables the agent to learn which principles work best for this user
        and adapt future recommendations accordingly.

        Args:
            principle_id: The ID of the principle used.
            success: Whether the intervention was successful.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> memory.record_intervention_feedback("friction_increase", True)
            >>> memory.record_intervention_feedback("friction_increase", True)
            >>> feedback = memory.intervention_feedback["friction_increase"]
            >>> print(f"Success rate: {feedback['successes']}/{feedback['total']}")
        """
        if principle_id not in self.intervention_feedback:
            self.intervention_feedback[principle_id] = InterventionFeedback(
                successes=0,
                failures=0,
                total=0,
                success_rate=0.0,
            )

        feedback = self.intervention_feedback[principle_id]
        feedback.total += 1

        if success:
            feedback.successes += 1
        else:
            feedback.failures += 1

        # Calculate success rate
        feedback.success_rate = feedback.successes / feedback.total

    def get_most_effective_principles(
        self, min_uses: int = 2
    ) -> list[tuple[str, float]]:
        """
        Get principles ranked by effectiveness for this user.

        TODO: Add test coverage for this method. Tests should verify:
        1. Filtering by minimum usage threshold (`min_uses` parameter)
        2. Correct sorting by success rate (descending)
        3. Returns empty list when no principles meet threshold
        4. Returns correct tuples of (principle_id, success_rate)

        Args:
            min_uses: Minimum number of times a principle must have been used.

        Returns:
            list[tuple[str, float]]: List of (principle_id, success_rate) tuples,
                                     sorted by success rate descending.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> memory.record_intervention_feedback("friction_increase", True)
            >>> memory.record_intervention_feedback("friction_increase", True)
            >>> effective = memory.get_most_effective_principles(min_uses=1)
            >>> print(effective[0])  # ('friction_increase', 1.0)
        """
        principles = []

        for principle_id, feedback in self.intervention_feedback.items():
            if feedback.total >= min_uses:
                principles.append((principle_id, feedback.success_rate))

        # Sort by success rate descending
        principles.sort(key=lambda x: x[1], reverse=True)

        return principles


def build_memory_summary(memory: UserMemory, include_profile: bool = True) -> str:
    """
    Build a text-based summary of user memory patterns and progress.

    This function analyzes the user's memory state to provide quick insights
    about their current habit streaks, struggles, and patterns. It's useful
    for generating session summaries or providing analytics feedback.

    Args:
        memory: UserMemory instance containing user's goals, streaks, and history.
        include_profile: Whether to include user profile hints for personalization.

    Returns:
        str: A formatted text summary covering current streaks, struggle counts,
             recent struggle patterns, and optionally profile information.

    Example:
        >>> memory = UserMemory(user_id="user123")
        >>> memory.streaks = {"no_food_delivery": {"current": 7, "best": 10}}
        >>> memory.struggles = [{"description": "Weekend overspending", "count": 3}]
        >>> summary = build_memory_summary(memory)
        >>> print(summary)
        📊 Memory Summary
        ...
    """
    summary_parts = []
    summary_parts.append("📊 **Memory Summary**\n")
    summary_parts.append("=" * 50 + "\n")

    # Include user profile for personalization
    if include_profile and memory.user_profile:
        profile = memory.user_profile
        summary_parts.append("\n👤 **User Profile:**\n")
        summary_parts.append(f"  • Engagement: {profile.engagement_level.title()}\n")
        summary_parts.append(f"  • Preferred tone: {profile.preferred_tone.title()}\n")
        summary_parts.append(f"  • Learning pace: {profile.learning_speed.title()}\n")

    # Current streak status
    if memory.streaks:
        summary_parts.append("\n🔥 **Current Streaks:**\n")
        active_streaks = []
        broken_streaks = []

        for streak_name, streak_data in memory.streaks.items():
            current = streak_data.current
            best = streak_data.best
            streak_label = streak_name.replace("_", " ").title()

            if current > 0:
                active_streaks.append(f"  • {streak_label}: {current} days")
            else:
                broken_streaks.append(f"  • {streak_label}: Reset (best was {best})")

        if active_streaks:
            for streak in active_streaks:
                summary_parts.append(f"{streak} ✨\n")
        if broken_streaks:
            summary_parts.append("\n  **Rebuilding:**\n")
            for streak in broken_streaks:
                summary_parts.append(f"{streak} 💪\n")
    else:
        summary_parts.append("\n🔥 **Streaks:** No active streaks yet.\n")

    # Struggles summary
    total_struggles = len(memory.struggles)
    if total_struggles > 0:
        summary_parts.append(f"\n⚠️  **Struggles Recorded:** {total_struggles}\n")

        # Show most recent 3 struggles
        recent_struggles = sorted(
            memory.struggles,
            key=lambda s: s.last_noted,
            reverse=True,
        )[:3]

        if recent_struggles:
            summary_parts.append("\n  **Recent patterns:**\n")
            for struggle in recent_struggles:
                description = struggle.description
                count = struggle.count
                summary_parts.append(f"  • {description} ({count}x)\n")
    else:
        summary_parts.append("\n⚠️  **Struggles:** None recorded yet.\n")

    # Closing note
    summary_parts.append("\n" + "=" * 50 + "\n")

    return "".join(summary_parts)
