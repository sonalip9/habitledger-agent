"""
Business logic for memory-related operations.

This module separates business logic from the UserMemory data model,
providing service methods for recording interactions, feedback, and
analyzing memory patterns.
"""

from typing import Any

from .memory import UserMemory
from .models import StreakData, Struggle


class MemoryService:
    """Service class for memory-related business logic."""

    @staticmethod
    def record_interaction(memory: UserMemory, outcome: dict[str, Any]) -> None:
        """
        Record an interaction outcome to update streaks and struggles.

        This method updates the user's memory based on the outcome of an interaction.
        It can increment/reset streaks, add new struggles, or record interventions.

        Args:
            memory: UserMemory instance to update.
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
            >>> MemoryService.record_interaction(memory, outcome)
            >>> print(memory.streaks["no_food_delivery"].current)
            1
        """
        # Delegate to the existing implementation
        memory.record_interaction(outcome)

    @staticmethod
    def record_feedback(
        memory: UserMemory,
        principle_id: str,
        success: bool,
    ) -> None:
        """
        Record the effectiveness of an intervention based on a principle.

        This enables the agent to learn which principles work best for this user
        and adapt future recommendations accordingly.

        Args:
            memory: UserMemory instance to update.
            principle_id: The ID of the principle used.
            success: Whether the intervention was successful.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> MemoryService.record_feedback(memory, "friction_increase", True)
            >>> MemoryService.record_feedback(memory, "friction_increase", True)
            >>> feedback = memory.intervention_feedback["friction_increase"]
            >>> print(f"Success rate: {feedback.success_rate}")
            Success rate: 1.0
        """
        memory.record_intervention_feedback(principle_id, success)

    @staticmethod
    def calculate_principle_effectiveness(
        memory: UserMemory,
        principle_id: str,
    ) -> float:
        """
        Calculate the effectiveness (success rate) of a specific principle for this user.

        Args:
            memory: UserMemory instance.
            principle_id: The principle ID to check.

        Returns:
            float: Success rate between 0.0 and 1.0, or 0.5 if no data available.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> MemoryService.record_feedback(memory, "loss_aversion", True)
            >>> MemoryService.record_feedback(memory, "loss_aversion", False)
            >>> effectiveness = MemoryService.calculate_principle_effectiveness(
            ...     memory, "loss_aversion"
            ... )
            >>> print(effectiveness)
            0.5
        """
        if principle_id not in memory.intervention_feedback:
            return 0.5  # Default/neutral effectiveness

        feedback = memory.intervention_feedback[principle_id]
        return feedback.success_rate

    @staticmethod
    def get_recent_struggles(
        memory: UserMemory,
        limit: int = 5,
    ) -> list[Struggle]:
        """
        Get the most recent struggles, sorted by last_noted timestamp.

        Args:
            memory: UserMemory instance.
            limit: Maximum number of struggles to return (default: 5).

        Returns:
            list[Struggle]: List of recent struggles, most recent first.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> memory.struggles.append(Struggle(
            ...     description="Overspending on weekends",
            ...     first_noted="2024-01-01",
            ...     last_noted="2024-01-15",
            ...     count=3
            ... ))
            >>> recent = MemoryService.get_recent_struggles(memory, limit=3)
            >>> print(len(recent))
            1
        """
        sorted_struggles = sorted(
            memory.struggles,
            key=lambda s: s.last_noted,
            reverse=True,
        )
        return sorted_struggles[:limit]

    @staticmethod
    def get_active_streaks(memory: UserMemory) -> dict[str, StreakData]:
        """
        Get all currently active streaks (current > 0).

        Args:
            memory: UserMemory instance.

        Returns:
            dict[str, StreakData]: Dictionary of active streaks only.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> memory.streaks["no_delivery"] = StreakData(current=5, best=10)
            >>> memory.streaks["save_daily"] = StreakData(current=0, best=3)
            >>> active = MemoryService.get_active_streaks(memory)
            >>> print(len(active))
            1
        """
        return {
            name: streak
            for name, streak in memory.streaks.items()
            if streak.current > 0
        }

    @staticmethod
    def get_broken_streaks(memory: UserMemory) -> dict[str, StreakData]:
        """
        Get all broken streaks (current = 0 but best > 0).

        Args:
            memory: UserMemory instance.

        Returns:
            dict[str, StreakData]: Dictionary of broken streaks that can be rebuilt.

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> memory.streaks["no_delivery"] = StreakData(current=0, best=10)
            >>> broken = MemoryService.get_broken_streaks(memory)
            >>> print(len(broken))
            1
        """
        return {
            name: streak
            for name, streak in memory.streaks.items()
            if streak.current == 0 and streak.best > 0
        }

    @staticmethod
    def get_principle_usage_count(memory: UserMemory, principle_id: str) -> int:
        """
        Get the number of times a principle has been used with this user.

        Args:
            memory: UserMemory instance.
            principle_id: The principle ID to check.

        Returns:
            int: Number of times the principle has been used (0 if never used).

        Example:
            >>> memory = UserMemory(user_id="user123")
            >>> MemoryService.record_feedback(memory, "friction_increase", True)
            >>> count = MemoryService.get_principle_usage_count(memory, "friction_increase")
            >>> print(count)
            1
        """
        if principle_id not in memory.intervention_feedback:
            return 0

        return memory.intervention_feedback[principle_id].total
