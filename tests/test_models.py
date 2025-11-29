"""
Tests for domain models in src/models.py.

This module tests dataclass validation, serialization/deserialization,
and type correctness of all domain models.
"""

from src.memory import UserProfile
from src.models import (
    AnalysisResult,
    BehaviouralPrinciple,
    BehaviourDatabase,
    ConversationRole,
    ConversationTurn,
    Goal,
    InterventionFeedback,
    StreakData,
    Struggle,
)


class TestGoal:
    """Tests for Goal model."""

    def test_goal_creation(self):
        """Test creating a Goal instance."""
        goal = Goal(description="Save ₹5000/month", target="₹60000/year")
        assert goal.description == "Save ₹5000/month"
        assert goal.target == "₹60000/year"
        assert not goal.completed
        assert goal.created_at is not None

    def test_goal_to_dict(self):
        """Test Goal serialization to dict."""
        goal = Goal(description="Test goal")
        data = goal.to_dict()
        assert data["description"] == "Test goal"
        assert "created_at" in data
        assert "completed" in data

    def test_goal_from_dict(self):
        """Test Goal deserialization from dict."""
        data = {
            "description": "Test goal",
            "target": "₹10000",
            "completed": True,
        }
        goal = Goal.from_dict(data)
        assert goal.description == "Test goal"
        assert goal.target == "₹10000"
        assert goal.completed


class TestStreakData:
    """Tests for StreakData model."""

    def test_streak_creation(self):
        """Test creating a StreakData instance."""
        streak = StreakData(current=5, best=10)
        assert streak.current == 5
        assert streak.best == 10
        assert streak.last_updated is not None

    def test_streak_to_dict(self):
        """Test StreakData serialization."""
        streak = StreakData(current=7, best=12)
        data = streak.to_dict()
        assert data["current"] == 7
        assert data["best"] == 12
        assert "last_updated" in data

    def test_streak_from_dict(self):
        """Test StreakData deserialization."""
        data = {"current": 3, "best": 8, "last_updated": "2024-01-01"}
        streak = StreakData.from_dict(data)
        assert streak.current == 3
        assert streak.best == 8
        assert streak.last_updated == "2024-01-01"


class TestStruggle:
    """Tests for Struggle model."""

    def test_struggle_creation(self):
        """Test creating a Struggle instance."""
        struggle = Struggle(description="Weekend overspending", count=3)
        assert struggle.description == "Weekend overspending"
        assert struggle.count == 3
        assert struggle.first_noted is not None
        assert struggle.last_noted is not None

    def test_struggle_serialization(self):
        """Test Struggle serialization round-trip."""
        struggle = Struggle(description="Impulse buying")
        data = struggle.to_dict()
        restored = Struggle.from_dict(data)
        assert restored.description == struggle.description
        assert restored.count == struggle.count


class TestConversationTurn:
    """Tests for ConversationTurn model."""

    def test_conversation_turn_creation(self):
        """Test creating a ConversationTurn instance."""
        turn = ConversationTurn(
            role=ConversationRole.USER,
            content="I need help with saving",
        )
        assert turn.role == ConversationRole.USER
        assert turn.content == "I need help with saving"
        assert turn.timestamp is not None

    def test_conversation_turn_with_metadata(self):
        """Test ConversationTurn with metadata."""
        turn = ConversationTurn(
            role=ConversationRole.ASSISTANT,
            content="Here's a suggestion",
            metadata={"principle_id": "loss_aversion", "confidence": 0.8},
        )
        assert turn.metadata["principle_id"] == "loss_aversion"
        assert turn.metadata["confidence"] == 0.8

    def test_conversation_turn_serialization(self):
        """Test ConversationTurn serialization."""
        turn = ConversationTurn(
            role=ConversationRole.USER,
            content="Test message",
        )
        data = turn.to_dict()
        assert data["role"] == "user"
        assert data["content"] == "Test message"

        restored = ConversationTurn.from_dict(data)
        assert restored.role == ConversationRole.USER
        assert restored.content == "Test message"


class TestInterventionFeedback:
    """Tests for InterventionFeedback model."""

    def test_feedback_creation(self):
        """Test creating an InterventionFeedback instance."""
        feedback = InterventionFeedback(
            successes=3,
            failures=1,
            total=4,
            success_rate=0.75,
        )
        assert feedback.successes == 3
        assert feedback.failures == 1
        assert feedback.total == 4
        assert feedback.success_rate == 0.75

    def test_feedback_serialization(self):
        """Test InterventionFeedback serialization."""
        feedback = InterventionFeedback(
            successes=2, failures=1, total=3, success_rate=0.67
        )
        data = feedback.to_dict()
        restored = InterventionFeedback.from_dict(data)
        assert restored.successes == feedback.successes
        assert restored.total == feedback.total


class TestBehaviouralPrinciple:
    """Tests for BehaviouralPrinciple model."""

    def test_principle_creation(self):
        """Test creating a BehaviouralPrinciple instance."""
        principle = BehaviouralPrinciple(
            id="loss_aversion",
            name="Loss Aversion",
            description="People feel losses more strongly",
            typical_triggers=["regret", "lose"],
            interventions=["Track streaks", "Visualize losses"],
        )
        assert principle.id == "loss_aversion"
        assert principle.name == "Loss Aversion"
        assert len(principle.typical_triggers) == 2
        assert len(principle.interventions) == 2

    def test_principle_serialization(self):
        """Test BehaviouralPrinciple serialization."""
        principle = BehaviouralPrinciple(
            id="test_principle",
            name="Test",
            description="Test description",
            typical_triggers=["trigger1"],
            interventions=["intervention1"],
        )
        data = principle.to_dict()
        restored = BehaviouralPrinciple.from_dict(data)
        assert restored.id == principle.id
        assert restored.name == principle.name


class TestBehaviourDatabase:
    """Tests for BehaviourDatabase model."""

    def test_database_creation(self, sample_behaviour_db):
        """Test creating a BehaviourDatabase instance."""
        db = BehaviourDatabase.from_dict(sample_behaviour_db)
        assert db.version == "1.0"
        assert len(db.principles) == 3

    def test_get_principle_by_id(self, sample_behaviour_database):
        """Test retrieving a principle by ID."""
        db = sample_behaviour_database
        principle = db.get_principle_by_id("loss_aversion")
        assert principle is not None
        assert principle.name == "Loss Aversion"

        not_found = db.get_principle_by_id("nonexistent")
        assert not_found is None

    def test_database_serialization(self, sample_behaviour_database):
        """Test BehaviourDatabase serialization."""
        db = sample_behaviour_database
        data = db.to_dict()
        restored = BehaviourDatabase.from_dict(data)
        assert len(restored.principles) == len(db.principles)
        assert restored.version == db.version


class TestAnalysisResult:
    """Tests for AnalysisResult model."""

    def test_analysis_result_creation(self):
        """Test creating an AnalysisResult instance."""
        result = AnalysisResult(
            detected_principle_id="friction_increase",
            reason="User mentioned food delivery",
            intervention_suggestions=["Delete apps", "Remove cards"],
            triggers_matched=["delivery", "food"],
            source="adk",
            confidence=0.85,
        )
        assert result.detected_principle_id == "friction_increase"
        assert result.confidence == 0.85
        assert len(result.intervention_suggestions) == 2

    def test_analysis_result_serialization(self):
        """Test AnalysisResult serialization."""
        result = AnalysisResult(
            detected_principle_id="loss_aversion",
            reason="Test reason",
            intervention_suggestions=["Test intervention"],
            triggers_matched=["test"],
            source="keyword",
            confidence=0.7,
        )
        data = result.to_dict()
        restored = AnalysisResult.from_dict(data)
        assert restored.detected_principle_id == result.detected_principle_id
        assert restored.confidence == result.confidence


class TestUserProfile:
    """Tests for UserProfile class."""

    def test_default_initialization(self):
        """Test UserProfile initialization with correct default values."""
        profile = UserProfile()
        assert profile.motivation_style == "unknown"
        assert profile.risk_tolerance == "medium"
        assert profile.engagement_level == "medium"
        assert profile.preferred_tone == "supportive"
        assert profile.learning_speed == "moderate"

    def test_custom_initialization(self):
        """Test UserProfile initialization with custom values."""
        profile = UserProfile(
            motivation_style="achievement",
            risk_tolerance="high",
            engagement_level="high",
            preferred_tone="direct",
            learning_speed="fast",
        )
        assert profile.motivation_style == "achievement"
        assert profile.risk_tolerance == "high"
        assert profile.engagement_level == "high"
        assert profile.preferred_tone == "direct"
        assert profile.learning_speed == "fast"

    def test_to_dict_serialization(self):
        """Test to_dict() serialization produces correct structure."""
        profile = UserProfile(
            motivation_style="achievement",
            risk_tolerance="low",
            engagement_level="high",
            preferred_tone="educational",
            learning_speed="slow",
        )
        data = profile.to_dict()

        assert isinstance(data, dict)
        assert data["motivation_style"] == "achievement"
        assert data["risk_tolerance"] == "low"
        assert data["engagement_level"] == "high"
        assert data["preferred_tone"] == "educational"
        assert data["learning_speed"] == "slow"

    def test_from_dict_deserialization_complete(self):
        """Test from_dict() deserialization with all fields."""
        data = {
            "motivation_style": "social",
            "risk_tolerance": "high",
            "engagement_level": "low",
            "preferred_tone": "direct",
            "learning_speed": "fast",
        }
        profile = UserProfile.from_dict(data)

        assert profile.motivation_style == "social"
        assert profile.risk_tolerance == "high"
        assert profile.engagement_level == "low"
        assert profile.preferred_tone == "direct"
        assert profile.learning_speed == "fast"

    def test_from_dict_deserialization_missing_fields(self):
        """Test from_dict() deserialization handles missing fields with defaults."""
        data = {
            "motivation_style": "fear_avoidance",
        }
        profile = UserProfile.from_dict(data)

        assert profile.motivation_style == "fear_avoidance"
        assert profile.risk_tolerance == "medium"  # Default
        assert profile.engagement_level == "medium"  # Default
        assert profile.preferred_tone == "supportive"  # Default
        assert profile.learning_speed == "moderate"  # Default

    def test_from_dict_deserialization_empty(self):
        """Test from_dict() deserialization with empty dictionary uses all defaults."""
        data = {}
        profile = UserProfile.from_dict(data)

        assert profile.motivation_style == "unknown"
        assert profile.risk_tolerance == "medium"
        assert profile.engagement_level == "medium"
        assert profile.preferred_tone == "supportive"
        assert profile.learning_speed == "moderate"

    def test_update_from_interaction_engagement_increase_low_to_medium(self):
        """Test update_from_interaction() increases engagement from low to medium."""
        profile = UserProfile(engagement_level="low")
        outcome = {"engaged": True}

        profile.update_from_interaction(outcome)
        assert profile.engagement_level == "medium"

    def test_update_from_interaction_engagement_increase_medium_to_high(self):
        """Test update_from_interaction() increases engagement from medium to high."""
        profile = UserProfile(engagement_level="medium")
        outcome = {"engaged": True}

        profile.update_from_interaction(outcome)
        assert profile.engagement_level == "high"

    def test_update_from_interaction_engagement_stays_at_high(self):
        """Test update_from_interaction() keeps engagement at high (no overflow)."""
        profile = UserProfile(engagement_level="high")
        outcome = {"engaged": True}

        profile.update_from_interaction(outcome)
        assert profile.engagement_level == "high"

    def test_update_from_interaction_learning_speed_slow_to_moderate(self):
        """Test update_from_interaction() increases learning speed from slow to moderate."""
        profile = UserProfile(learning_speed="slow")
        outcome = {"intervention_successful": True}

        profile.update_from_interaction(outcome)
        assert profile.learning_speed == "moderate"

    def test_update_from_interaction_learning_speed_moderate_to_fast(self):
        """Test update_from_interaction() increases learning speed from moderate to fast."""
        profile = UserProfile(learning_speed="moderate")
        outcome = {"intervention_successful": True}

        profile.update_from_interaction(outcome)
        assert profile.learning_speed == "fast"

    def test_update_from_interaction_learning_speed_stays_at_fast(self):
        """Test update_from_interaction() keeps learning speed at fast (no overflow)."""
        profile = UserProfile(learning_speed="fast")
        outcome = {"intervention_successful": True}

        profile.update_from_interaction(outcome)
        assert profile.learning_speed == "fast"

    def test_update_from_interaction_no_changes(self):
        """Test update_from_interaction() with no relevant outcome keys."""
        profile = UserProfile(engagement_level="low", learning_speed="slow")
        outcome = {}

        profile.update_from_interaction(outcome)
        assert profile.engagement_level == "low"  # Unchanged
        assert profile.learning_speed == "slow"  # Unchanged

    def test_update_from_interaction_combined_updates(self):
        """Test update_from_interaction() updates both engagement and learning speed."""
        profile = UserProfile(engagement_level="low", learning_speed="slow")
        outcome = {"engaged": True, "intervention_successful": True}

        profile.update_from_interaction(outcome)
        assert profile.engagement_level == "medium"
        assert profile.learning_speed == "moderate"

    def test_serialization_round_trip(self):
        """Test complete serialization round-trip."""
        original = UserProfile(
            motivation_style="achievement",
            risk_tolerance="high",
            engagement_level="medium",
            preferred_tone="direct",
            learning_speed="fast",
        )

        data = original.to_dict()
        restored = UserProfile.from_dict(data)

        assert restored.motivation_style == original.motivation_style
        assert restored.risk_tolerance == original.risk_tolerance
        assert restored.engagement_level == original.engagement_level
        assert restored.preferred_tone == original.preferred_tone
        assert restored.learning_speed == original.learning_speed
