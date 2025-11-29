"""
Pytest fixtures and configuration for HabitLedger tests.

This module provides reusable test fixtures for creating sample data
including behaviour databases, user memory instances, and test scenarios.
"""

import pytest

from src.config import load_env
from src.memory import UserMemory
from src.models import (
    BehaviourDatabase,
    Goal,
    InterventionFeedback,
    StreakData,
    Struggle,
)

# Load environment variables at test startup
load_env()


@pytest.fixture
def sample_behaviour_db() -> dict:
    """Create a sample behaviour database for testing."""
    return {
        "version": "1.0",
        "description": "Test behaviour principles database",
        "principles": [
            {
                "id": "loss_aversion",
                "name": "Loss Aversion",
                "description": "People feel losses more strongly than gains",
                "typical_triggers": ["regret", "lose", "failed", "broke my streak"],
                "interventions": [
                    "Track and visualize what you'd lose by breaking your savings streak",
                    "Calculate the opportunity cost of impulse purchases",
                ],
            },
            {
                "id": "friction_increase",
                "name": "Friction Increase",
                "description": "Make bad habits harder to do",
                "typical_triggers": [
                    "too easy",
                    "one click",
                    "delivery",
                    "food delivery",
                ],
                "interventions": [
                    "Delete food delivery and shopping apps from your phone",
                    "Remove saved payment info from online shopping sites",
                ],
            },
            {
                "id": "habit_loops",
                "name": "Habit Loops",
                "description": "Habits follow cue, routine, reward pattern",
                "typical_triggers": ["always", "every time", "whenever", "stress"],
                "interventions": [
                    "Identify your impulse spending cues",
                    "Replace bad routine with healthier alternative",
                ],
            },
        ],
    }


@pytest.fixture
def sample_behaviour_database(
    sample_behaviour_db: dict,  # noqa: R504
) -> BehaviourDatabase:
    """Create a typed BehaviourDatabase instance."""
    return BehaviourDatabase.from_dict(sample_behaviour_db)


@pytest.fixture
def empty_memory() -> UserMemory:
    """Create an empty UserMemory instance for testing."""
    return UserMemory(user_id="test_user")


@pytest.fixture
def populated_memory() -> UserMemory:
    """Create a UserMemory instance with sample data."""
    memory = UserMemory(user_id="test_user")

    # Add goals
    memory.goals = [
        Goal(description="Save ₹5000/month", target="₹60000/year"),
        Goal(description="Reduce food delivery spending"),
    ]

    # Add streaks
    memory.streaks = {
        "no_food_delivery": StreakData(current=7, best=14),
        "daily_savings": StreakData(current=0, best=30),
    }

    # Add struggles
    memory.struggles = [
        Struggle(
            description="Weekend overspending",
            first_noted="2024-01-01",
            last_noted="2024-01-15",
            count=3,
        ),
        Struggle(
            description="Impulse buying during sales",
            first_noted="2024-01-10",
            last_noted="2024-01-20",
            count=2,
        ),
    ]

    # Add intervention feedback
    memory.intervention_feedback = {
        "friction_increase": InterventionFeedback(
            successes=3, failures=1, total=4, success_rate=0.75
        ),
        "loss_aversion": InterventionFeedback(
            successes=1, failures=1, total=2, success_rate=0.5
        ),
    }

    return memory


@pytest.fixture
def sample_user_input() -> dict[str, str]:
    """Sample user inputs for different scenarios."""
    return {
        "food_delivery": "I keep ordering food delivery every evening when I'm stressed",
        "broken_streak": "I broke my savings streak and feel terrible about it",
        "vague": "I need help with my finances",
        "habit_trigger": "Every time I come home from work, I order food without thinking",
    }
