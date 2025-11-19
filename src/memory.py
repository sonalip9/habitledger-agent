"""
Simple memory and persistence utilities.

This module manages user data persistence including goals, habit streaks,
and conversation history for the HabitLedger agent.

The UserMemory class provides a single-responsibility interface for storing
and retrieving user state without mixing in business logic or behaviour analysis.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


class UserMemory:
    """
    Manages persistent memory state for a single user.

    This class tracks user goals, habit streaks, struggles, and interaction history.
    It provides serialization/deserialization to/from JSON files for persistence.

    The class focuses solely on data storage and retrieval, avoiding business logic
    about habit analysis or intervention strategies (which belong in behaviour_engine.py).

    Attributes:
        user_id (str): Unique identifier for the user.
        goals (list[dict]): List of user financial goals.
        streaks (dict): Dictionary tracking habit streaks (e.g., no_food_delivery).
        struggles (list[dict]): List of recorded user struggles with dates.
        interventions (list[dict]): History of suggested interventions.
        last_check_in (str): ISO format timestamp of last interaction.
        behaviour_patterns (dict): Detected patterns (e.g., end_of_month_overspending).

    Example:
        >>> memory = UserMemory(user_id="user123")
        >>> memory.goals.append({"type": "savings", "target": "Save ₹5000/month"})
        >>> memory.save_to_file("data/user123.json")
        >>> loaded = UserMemory.load_from_file("data/user123.json")
    """

    def __init__(
        self,
        user_id: str = "default_user",
        goals: Optional[list[dict]] = None,
        streaks: Optional[dict[str, dict]] = None,
        struggles: Optional[list[dict]] = None,
        interventions: Optional[list[dict]] = None,
        last_check_in: Optional[str] = None,
        behaviour_patterns: Optional[dict] = None,
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
            "goals": self.goals,
            "streaks": self.streaks,
            "struggles": self.struggles,
            "interventions": self.interventions,
            "last_check_in": self.last_check_in,
            "behaviour_patterns": self.behaviour_patterns,
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
        return cls(
            user_id=data.get("user_id", "default_user"),
            goals=data.get("goals", []),
            streaks=data.get("streaks", {}),
            struggles=data.get("struggles", []),
            interventions=data.get("interventions", []),
            last_check_in=data.get("last_check_in"),
            behaviour_patterns=data.get("behaviour_patterns", {}),
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
                    self.streaks[streak_name] = {
                        "current": 0,
                        "best": 0,
                        "last_updated": timestamp,
                    }

                if success:
                    self.streaks[streak_name]["current"] += 1
                    if (
                        self.streaks[streak_name]["current"]
                        > self.streaks[streak_name]["best"]
                    ):
                        self.streaks[streak_name]["best"] = self.streaks[streak_name][
                            "current"
                        ]
                else:
                    self.streaks[streak_name]["current"] = 0

                self.streaks[streak_name]["last_updated"] = timestamp

        elif outcome_type == "struggle":
            description = outcome.get("description", "")
            if description:
                # Check if this struggle already exists
                existing = next(
                    (s for s in self.struggles if s.get("description") == description),
                    None,
                )
                if existing:
                    existing["count"] = existing.get("count", 1) + 1
                    existing["last_noted"] = timestamp
                else:
                    self.struggles.append(
                        {
                            "description": description,
                            "first_noted": timestamp,
                            "last_noted": timestamp,
                            "count": 1,
                        }
                    )

        elif outcome_type == "intervention":
            self.interventions.append(
                {
                    "date": timestamp,
                    "type": outcome.get("principle_id", "unknown"),
                    "description": outcome.get("description", ""),
                }
            )

        # Update last check-in timestamp
        self.last_check_in = timestamp
