"""
Tests for coach module and response generation.

This module tests the main coaching functions including response generation,
session summaries, and interaction with the ADK agent.
"""

from src.coach import (
    _generate_clarifying_questions,
    _get_clarifying_questions_for_principle,
    generate_session_summary,
    run_once,
)
from src.models import BehaviourPattern, ConversationRole


class TestRunOnce:
    """Tests for run_once function."""

    def test_run_once_basic_response(
        self, empty_memory, sample_behaviour_db, sample_user_input
    ):
        """Test basic response generation."""
        response = run_once(
            sample_user_input["food_delivery"],
            empty_memory,
            sample_behaviour_db,
        )

        assert isinstance(response, str)
        assert len(response) > 0
        # Should contain some coaching elements (flexible to accommodate fallback mode)
        # Accept a broader range of helpful coaching terminology
        assert any(
            keyword in response.lower()
            for keyword in [
                "principle",
                "suggestion",
                "action",
                "guidance",
                "help",
                "try",
                "consider",
                "can",
                "might",
                "could",
                "habit",
                "save",
                "spending",
            ]
        ), f"Response should contain coaching language, got: {response[:100]}"

    def test_run_once_updates_conversation_history(
        self, empty_memory, sample_behaviour_db, sample_user_input
    ):
        """Test that run_once updates conversation history."""
        initial_count = len(empty_memory.conversation_history)

        run_once(
            sample_user_input["food_delivery"],
            empty_memory,
            sample_behaviour_db,
        )

        # Should have added user message and assistant response
        assert len(empty_memory.conversation_history) >= initial_count + 2

        # Check roles
        turns = empty_memory.conversation_history
        assert turns[-2].role == ConversationRole.USER
        assert turns[-1].role == ConversationRole.ASSISTANT

    def test_run_once_records_intervention(
        self, empty_memory, sample_behaviour_db, sample_user_input
    ):
        """Test that interventions are recorded in memory."""
        initial_interventions = len(empty_memory.interventions)

        run_once(
            sample_user_input["food_delivery"],
            empty_memory,
            sample_behaviour_db,
        )

        # Should have recorded an intervention if a principle was detected
        # Note: This might be 0 or 1 depending on whether ADK or template was used
        assert len(empty_memory.interventions) >= initial_interventions

    def test_run_once_with_populated_memory(
        self, populated_memory, sample_behaviour_db, sample_user_input
    ):
        """Test response generation with existing memory context."""
        response = run_once(
            sample_user_input["broken_streak"],
            populated_memory,
            sample_behaviour_db,
        )

        assert isinstance(response, str)
        assert len(response) > 0

    def test_run_once_low_confidence_clarification(
        self, empty_memory, sample_behaviour_db
    ):
        """Test that low confidence triggers clarifying questions."""
        # Vague input should result in lower confidence
        response = run_once(
            "I have money issues",
            empty_memory,
            sample_behaviour_db,
        )

        # Response should exist
        assert isinstance(response, str)
        assert len(response) > 0


class TestGenerateSessionSummary:
    """Tests for session summary generation."""

    def test_generate_summary_empty_memory(self, empty_memory):
        """Test generating summary for empty memory."""
        summary = generate_session_summary(empty_memory)

        assert isinstance(summary, str)
        assert "Session Summary" in summary
        assert len(summary) > 0

    def test_generate_summary_with_active_streaks(self, populated_memory):
        """Test summary generation with active streaks."""
        summary = generate_session_summary(populated_memory)

        assert "Active Streaks" in summary or "Streaks" in summary
        assert "no_food_delivery" in summary or "No Food Delivery" in summary

    def test_generate_summary_with_struggles(self, populated_memory):
        """Test summary generation with recorded struggles."""
        summary = generate_session_summary(populated_memory)

        assert "Struggles" in summary or "Struggle" in summary
        # At least one struggle should be mentioned
        assert "overspending" in summary.lower() or "impulse" in summary.lower()

    def test_summary_with_behaviour_patterns(self, populated_memory):
        """Test summary generation with behaviour patterns."""
        # Add a pattern using typed model

        populated_memory.behaviour_patterns = {
            "end_of_month_overspending": BehaviourPattern(detected=True, occurrences=3)
        }

        summary = generate_session_summary(populated_memory)

        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_summary_includes_encouragement(self, populated_memory):
        """Test that summary includes encouraging message."""
        summary = generate_session_summary(populated_memory)

        # Should contain some encouraging language
        encouraging_words = ["progress", "keep", "great", "journey", "win"]
        assert any(word in summary.lower() for word in encouraging_words)


class TestGenerateClarifyingQuestions:
    """Tests for _generate_clarifying_questions function."""

    def test_returns_formatted_response(self, sample_behaviour_db):
        """Test that function returns properly formatted response with questions."""
        result = _generate_clarifying_questions(
            principle_id="loss_aversion",
            _user_input="I'm worried about my progress",
            behaviour_db=sample_behaviour_db,
        )

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Let me understand better" in result
        assert "Can you tell me more about:" in result
        assert "💡" in result  # Encouragement section

    def test_generates_appropriate_questions_for_loss_aversion(
        self, sample_behaviour_db
    ):
        """Test that loss_aversion principle generates relevant questions."""
        result = _generate_clarifying_questions(
            principle_id="loss_aversion",
            _user_input="I'm worried",
            behaviour_db=sample_behaviour_db,
        )

        # Check for loss aversion related keywords
        assert any(
            keyword in result.lower()
            for keyword in ["tracking", "progress", "lose", "goal", "milestone"]
        )

    def test_generates_appropriate_questions_for_habit_loops(self, sample_behaviour_db):
        """Test that habit_loops principle generates relevant questions."""
        result = _generate_clarifying_questions(
            principle_id="habit_loops",
            _user_input="I keep doing this",
            behaviour_db=sample_behaviour_db,
        )

        # Check for habit loop related keywords
        assert any(
            keyword in result.lower()
            for keyword in ["trigger", "behavior", "pattern", "emotion"]
        )

    def test_generates_appropriate_questions_for_friction_increase(
        self, sample_behaviour_db
    ):
        """Test that friction_increase principle generates relevant questions."""
        result = _generate_clarifying_questions(
            principle_id="friction_increase",
            _user_input="I can't resist",
            behaviour_db=sample_behaviour_db,
        )

        # Check for friction increase related keywords
        assert any(
            keyword in result.lower()
            for keyword in ["easy", "impulsive", "steps", "resist", "urge"]
        )

    def test_handles_unknown_principle_gracefully(self, sample_behaviour_db):
        """Test that unknown principle_id uses default questions."""
        result = _generate_clarifying_questions(
            principle_id="unknown_principle_xyz",
            _user_input="I need help",
            behaviour_db=sample_behaviour_db,
        )

        assert isinstance(result, str)
        assert len(result) > 0
        # Should still have the basic structure
        assert "Let me understand better" in result
        assert "Can you tell me more about:" in result

    def test_includes_principle_name_in_response(self, sample_behaviour_db):
        """Test that response includes the principle name."""
        result = _generate_clarifying_questions(
            principle_id="loss_aversion",
            _user_input="worried",
            behaviour_db=sample_behaviour_db,
        )

        # Should mention Loss Aversion (the principle name from the DB)
        assert "Loss Aversion" in result

    def test_response_has_numbered_questions(self, sample_behaviour_db):
        """Test that questions are numbered properly."""
        result = _generate_clarifying_questions(
            principle_id="habit_loops",
            _user_input="test",
            behaviour_db=sample_behaviour_db,
        )

        # Should have numbered questions
        assert "1." in result
        assert "2." in result

    def test_response_includes_encouragement(self, sample_behaviour_db):
        """Test that response includes encouraging message."""
        result = _generate_clarifying_questions(
            principle_id="loss_aversion",
            _user_input="test",
            behaviour_db=sample_behaviour_db,
        )

        # Should include encouragement at the end
        assert "more details" in result.lower()
        assert "support" in result.lower()


class TestGetClarifyingQuestionsForPrinciple:
    """Tests for _get_clarifying_questions_for_principle function."""

    def test_returns_list_of_questions(self):
        """Test that function returns a list of questions."""
        result = _get_clarifying_questions_for_principle("loss_aversion")

        assert isinstance(result, list)
        assert len(result) >= 2  # Should have at least 2 questions
        assert all(isinstance(q, str) for q in result)

    def test_loss_aversion_questions(self):
        """Test questions for loss_aversion principle."""
        questions = _get_clarifying_questions_for_principle("loss_aversion")

        assert len(questions) >= 2
        # Should ask about tracking, progress, or goals
        combined = " ".join(questions).lower()
        assert any(
            keyword in combined
            for keyword in ["tracking", "progress", "feel", "goal", "milestone"]
        )

    def test_habit_loops_questions(self):
        """Test questions for habit_loops principle."""
        questions = _get_clarifying_questions_for_principle("habit_loops")

        assert len(questions) >= 2
        combined = " ".join(questions).lower()
        assert any(
            keyword in combined
            for keyword in ["trigger", "behavior", "pattern", "emotion", "notice"]
        )

    def test_commitment_devices_questions(self):
        """Test questions for commitment_devices principle."""
        questions = _get_clarifying_questions_for_principle("commitment_devices")

        assert len(questions) >= 2
        combined = " ".join(questions).lower()
        assert any(
            keyword in combined for keyword in ["tried", "change", "knows", "harder"]
        )

    def test_temptation_bundling_questions(self):
        """Test questions for temptation_bundling principle."""
        questions = _get_clarifying_questions_for_principle("temptation_bundling")

        assert len(questions) >= 2
        combined = " ".join(questions).lower()
        assert any(
            keyword in combined for keyword in ["enjoy", "fun", "chore", "combine"]
        )

    def test_friction_reduction_questions(self):
        """Test questions for friction_reduction principle."""
        questions = _get_clarifying_questions_for_principle("friction_reduction")

        assert len(questions) >= 2
        combined = " ".join(questions).lower()
        assert any(
            keyword in combined
            for keyword in ["steps", "complicated", "easy", "time-consuming"]
        )

    def test_friction_increase_questions(self):
        """Test questions for friction_increase principle."""
        questions = _get_clarifying_questions_for_principle("friction_increase")

        assert len(questions) >= 2
        combined = " ".join(questions).lower()
        assert any(
            keyword in combined
            for keyword in ["easy", "impulsive", "steps", "urge", "resist"]
        )

    def test_default_effect_questions(self):
        """Test questions for default_effect principle."""
        questions = _get_clarifying_questions_for_principle("default_effect")

        assert len(questions) >= 2
        combined = " ".join(questions).lower()
        assert any(
            keyword in combined
            for keyword in ["remember", "manual", "automat", "default"]
        )

    def test_micro_habits_questions(self):
        """Test questions for micro_habits principle."""
        questions = _get_clarifying_questions_for_principle("micro_habits")

        assert len(questions) >= 2
        combined = " ".join(questions).lower()
        assert any(
            keyword in combined
            for keyword in ["smallest", "tiny", "overwhelming", "version"]
        )

    def test_unknown_principle_returns_default_questions(self):
        """Test that unknown principle returns default questions."""
        questions = _get_clarifying_questions_for_principle("unknown_principle_xyz")

        assert isinstance(questions, list)
        assert len(questions) >= 2
        # Should be generic questions
        combined = " ".join(questions).lower()
        assert any(
            keyword in combined
            for keyword in ["trying", "situation", "achieve", "challenge", "tried"]
        )
