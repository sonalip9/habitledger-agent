"""
Tests for MemoryService business logic.

This module tests memory-related business logic including recording
interactions, feedback tracking, and memory analysis operations.
"""

from src.memory_service import MemoryService


class TestMemoryService:
    """Tests for MemoryService methods."""

    def test_record_streak_success(self, empty_memory):
        """Test recording a successful streak update."""
        outcome = {
            "type": "streak_update",
            "streak_name": "no_food_delivery",
            "success": True,
        }
        MemoryService.record_interaction(empty_memory, outcome)

        assert "no_food_delivery" in empty_memory.streaks
        assert empty_memory.streaks["no_food_delivery"].current == 1
        assert empty_memory.streaks["no_food_delivery"].best == 1

    def test_record_streak_failure(self, populated_memory):
        """Test recording a failed streak (breaking streak)."""
        # Existing streak has current=7
        outcome = {
            "type": "streak_update",
            "streak_name": "no_food_delivery",
            "success": False,
        }
        MemoryService.record_interaction(populated_memory, outcome)

        assert populated_memory.streaks["no_food_delivery"].current == 0
        assert populated_memory.streaks["no_food_delivery"].best == 14  # Best unchanged

    def test_record_struggle_new(self, empty_memory):
        """Test recording a new struggle."""
        outcome = {
            "type": "struggle",
            "description": "Weekend overspending",
        }
        MemoryService.record_interaction(empty_memory, outcome)

        assert len(empty_memory.struggles) == 1
        assert empty_memory.struggles[0].description == "Weekend overspending"
        assert empty_memory.struggles[0].count == 1

    def test_record_struggle_duplicate(self, populated_memory):
        """Test recording a duplicate struggle increments count."""
        initial_count = len(populated_memory.struggles)
        outcome = {
            "type": "struggle",
            "description": "Weekend overspending",
        }
        MemoryService.record_interaction(populated_memory, outcome)

        assert len(populated_memory.struggles) == initial_count  # No new struggle added
        struggle = next(
            s
            for s in populated_memory.struggles
            if s.description == "Weekend overspending"
        )
        assert struggle.count == 4  # Was 3, now 4

    def test_record_feedback_new_principle(self, empty_memory):
        """Test recording feedback for a new principle."""
        MemoryService.record_feedback(empty_memory, "friction_increase", True)

        assert "friction_increase" in empty_memory.intervention_feedback
        feedback = empty_memory.intervention_feedback["friction_increase"]
        assert feedback.successes == 1
        assert feedback.total == 1
        assert feedback.success_rate == 1.0

    def test_record_feedback_existing_principle(self, populated_memory):
        """Test recording additional feedback for existing principle."""
        initial_total = populated_memory.intervention_feedback[
            "friction_increase"
        ].total

        MemoryService.record_feedback(populated_memory, "friction_increase", False)

        feedback = populated_memory.intervention_feedback["friction_increase"]
        assert feedback.total == initial_total + 1
        assert feedback.failures == 2  # Was 1, now 2
        assert feedback.success_rate == 3 / 5  # 3 successes out of 5 total

    def test_calculate_principle_effectiveness_existing(self, populated_memory):
        """Test calculating effectiveness for a tracked principle."""
        effectiveness = MemoryService.calculate_principle_effectiveness(
            populated_memory, "friction_increase"
        )
        assert effectiveness == 0.75

    def test_calculate_principle_effectiveness_new(self, empty_memory):
        """Test calculating effectiveness for an untracked principle."""
        effectiveness = MemoryService.calculate_principle_effectiveness(
            empty_memory, "unknown_principle"
        )
        assert effectiveness == 0.5  # Default neutral

    def test_get_recent_struggles(self, populated_memory):
        """Test retrieving recent struggles."""
        recent = MemoryService.get_recent_struggles(populated_memory, limit=1)

        assert len(recent) == 1
        assert recent[0].description == "Impulse buying during sales"  # Most recent

    def test_get_recent_struggles_empty(self, empty_memory):
        """Test retrieving struggles from empty memory."""
        recent = MemoryService.get_recent_struggles(empty_memory)
        assert len(recent) == 0

    def test_get_active_streaks(self, populated_memory):
        """Test retrieving active streaks."""
        active = MemoryService.get_active_streaks(populated_memory)

        assert len(active) == 1
        assert "no_food_delivery" in active
        assert active["no_food_delivery"].current == 7

    def test_get_broken_streaks(self, populated_memory):
        """Test retrieving broken streaks."""
        broken = MemoryService.get_broken_streaks(populated_memory)

        assert len(broken) == 1
        assert "daily_savings" in broken
        assert broken["daily_savings"].current == 0
        assert broken["daily_savings"].best == 30

    def test_get_principle_usage_count_existing(self, populated_memory):
        """Test getting usage count for a tracked principle."""
        count = MemoryService.get_principle_usage_count(
            populated_memory, "friction_increase"
        )
        assert count == 4

    def test_get_principle_usage_count_new(self, empty_memory):
        """Test getting usage count for an untracked principle."""
        count = MemoryService.get_principle_usage_count(empty_memory, "new_principle")
        assert count == 0


class TestUserMemoryInterventionFeedback:
    """Tests for UserMemory.record_intervention_feedback() method."""

    def test_record_intervention_feedback_new_principle(self, empty_memory):
        """Test creating new feedback entry for a principle."""
        empty_memory.record_intervention_feedback("friction_increase", True)

        assert "friction_increase" in empty_memory.intervention_feedback
        feedback = empty_memory.intervention_feedback["friction_increase"]
        assert feedback.successes == 1
        assert feedback.failures == 0
        assert feedback.total == 1
        assert feedback.success_rate == 1.0

    def test_record_intervention_feedback_increment_success(self, empty_memory):
        """Test incrementing success counts correctly."""
        empty_memory.record_intervention_feedback("loss_aversion", True)
        empty_memory.record_intervention_feedback("loss_aversion", True)

        feedback = empty_memory.intervention_feedback["loss_aversion"]
        assert feedback.successes == 2
        assert feedback.failures == 0
        assert feedback.total == 2
        assert feedback.success_rate == 1.0

    def test_record_intervention_feedback_increment_failure(self, empty_memory):
        """Test incrementing failure counts correctly."""
        empty_memory.record_intervention_feedback("habit_loops", False)
        empty_memory.record_intervention_feedback("habit_loops", False)

        feedback = empty_memory.intervention_feedback["habit_loops"]
        assert feedback.successes == 0
        assert feedback.failures == 2
        assert feedback.total == 2
        assert feedback.success_rate == 0.0

    def test_record_intervention_feedback_mixed_outcomes(self, empty_memory):
        """Test calculating success_rate accurately with mixed outcomes."""
        empty_memory.record_intervention_feedback("friction_increase", True)
        empty_memory.record_intervention_feedback("friction_increase", True)
        empty_memory.record_intervention_feedback("friction_increase", False)
        empty_memory.record_intervention_feedback("friction_increase", True)

        feedback = empty_memory.intervention_feedback["friction_increase"]
        assert feedback.successes == 3
        assert feedback.failures == 1
        assert feedback.total == 4
        assert feedback.success_rate == 0.75

    def test_record_intervention_feedback_accumulation(self, empty_memory):
        """Test multiple feedback recordings accumulate correctly."""
        # Record 10 interventions with varying success
        for i in range(10):
            success = i % 3 != 0  # i % 3 != 0 gives 6 successes out of 10
            empty_memory.record_intervention_feedback("test_principle", success)

        feedback = empty_memory.intervention_feedback["test_principle"]
        assert feedback.total == 10
        assert feedback.successes == 6
        assert feedback.failures == 4
        assert feedback.success_rate == 0.6

    def test_record_intervention_feedback_multiple_principles(self, empty_memory):
        """Test tracking feedback for multiple principles independently."""
        empty_memory.record_intervention_feedback("friction_increase", True)
        empty_memory.record_intervention_feedback("loss_aversion", False)
        empty_memory.record_intervention_feedback("friction_increase", True)

        assert len(empty_memory.intervention_feedback) == 2
        assert (
            empty_memory.intervention_feedback["friction_increase"].success_rate == 1.0
        )
        assert empty_memory.intervention_feedback["loss_aversion"].success_rate == 0.0


class TestUserMemoryMostEffectivePrinciples:
    """Tests for UserMemory.get_most_effective_principles() method."""

    def test_get_most_effective_principles_single_principle(self, empty_memory):
        """Test filtering with a single principle meeting threshold."""
        empty_memory.record_intervention_feedback("friction_increase", True)
        empty_memory.record_intervention_feedback("friction_increase", True)

        effective = empty_memory.get_most_effective_principles(min_uses=2)

        assert len(effective) == 1
        assert effective[0] == ("friction_increase", 1.0)

    def test_get_most_effective_principles_sorting(self, empty_memory):
        """Test correct sorting by success rate (descending)."""
        # Principle 1: 100% success
        empty_memory.record_intervention_feedback("principle_a", True)
        empty_memory.record_intervention_feedback("principle_a", True)

        # Principle 2: 75% success
        empty_memory.record_intervention_feedback("principle_b", True)
        empty_memory.record_intervention_feedback("principle_b", True)
        empty_memory.record_intervention_feedback("principle_b", True)
        empty_memory.record_intervention_feedback("principle_b", False)

        # Principle 3: 50% success
        empty_memory.record_intervention_feedback("principle_c", True)
        empty_memory.record_intervention_feedback("principle_c", False)

        effective = empty_memory.get_most_effective_principles(min_uses=2)

        assert len(effective) == 3
        assert effective[0][0] == "principle_a"
        assert effective[0][1] == 1.0
        assert effective[1][0] == "principle_b"
        assert effective[1][1] == 0.75
        assert effective[2][0] == "principle_c"
        assert effective[2][1] == 0.5

    def test_get_most_effective_principles_min_uses_filter(self, empty_memory):
        """Test filtering by minimum usage threshold (min_uses parameter)."""
        # Principle with 1 use (below threshold)
        empty_memory.record_intervention_feedback("principle_low", True)

        # Principle with 3 uses (meets threshold)
        empty_memory.record_intervention_feedback("principle_high", True)
        empty_memory.record_intervention_feedback("principle_high", True)
        empty_memory.record_intervention_feedback("principle_high", False)

        effective = empty_memory.get_most_effective_principles(min_uses=2)

        assert len(effective) == 1
        assert effective[0][0] == "principle_high"

    def test_get_most_effective_principles_empty_list(self, empty_memory):
        """Test returns empty list when no principles meet threshold."""
        # Add a principle with only 1 use
        empty_memory.record_intervention_feedback("test_principle", True)

        effective = empty_memory.get_most_effective_principles(min_uses=5)

        assert len(effective) == 0
        assert effective == []

    def test_get_most_effective_principles_no_feedback(self, empty_memory):
        """Test returns empty list when no feedback has been recorded."""
        effective = empty_memory.get_most_effective_principles(min_uses=1)

        assert len(effective) == 0
        assert effective == []

    def test_get_most_effective_principles_correct_tuples(self, empty_memory):
        """Test returns correct tuples of (principle_id, success_rate)."""
        empty_memory.record_intervention_feedback("test_principle", True)
        empty_memory.record_intervention_feedback("test_principle", False)

        effective = empty_memory.get_most_effective_principles(min_uses=2)

        assert len(effective) == 1
        principle_id, success_rate = effective[0]
        assert principle_id == "test_principle"
        assert success_rate == 0.5
        assert isinstance(principle_id, str)
        assert isinstance(success_rate, float)

    def test_get_most_effective_principles_default_min_uses(self, empty_memory):
        """Test default min_uses parameter of 2."""
        # Principle with 1 use (below default)
        empty_memory.record_intervention_feedback("principle_one", True)

        # Principle with 2 uses (meets default)
        empty_memory.record_intervention_feedback("principle_two", True)
        empty_memory.record_intervention_feedback("principle_two", True)

        # Call without specifying min_uses (should use default of 2)
        effective = empty_memory.get_most_effective_principles()

        assert len(effective) == 1
        assert effective[0][0] == "principle_two"

    def test_get_most_effective_principles_with_existing_feedback(
        self, populated_memory
    ):
        """Test with pre-populated memory containing feedback."""
        # populated_memory already has friction_increase (0.75) and loss_aversion (0.5)
        effective = populated_memory.get_most_effective_principles(min_uses=2)

        assert len(effective) == 2
        assert effective[0][0] == "friction_increase"
        assert effective[0][1] == 0.75
        assert effective[1][0] == "loss_aversion"
        assert effective[1][1] == 0.5
