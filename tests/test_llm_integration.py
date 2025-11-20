"""
Tests for LLM integration in behaviour analysis.

This module tests the LLM-based behaviour analysis functionality,
including the primary LLM path and keyword-based fallback.
"""

import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.behaviour_engine import analyse_behaviour, _analyse_behaviour_keyword
from src.llm_client import analyse_behaviour_with_llm, _build_memory_context
from src.memory import UserMemory


def get_test_behaviour_db():
    """Load the actual behaviour database for testing."""
    db_path = Path(__file__).parent.parent / "data" / "behaviour_principles.json"
    with open(db_path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestKeywordFallback:
    """Tests for keyword-based behaviour analysis (fallback)."""

    def test_friction_increase_detection(self):
        """Test that food delivery triggers friction_increase principle."""
        behaviour_db = get_test_behaviour_db()
        memory = UserMemory(user_id="test_user")

        result = _analyse_behaviour_keyword(
            "I keep ordering food delivery when stressed",
            memory,
            behaviour_db,
        )

        assert result["detected_principle_id"] == "friction_increase"
        assert "delivery" in result["triggers_matched"] or "food delivery" in result["triggers_matched"]
        assert len(result["intervention_suggestions"]) > 0

    def test_loss_aversion_with_streaks(self):
        """Test that loss aversion is detected with streak context."""
        behaviour_db = get_test_behaviour_db()
        memory = UserMemory(user_id="test_user")
        memory.streaks = {"savings_streak": {"current": 10, "best": 15}}

        result = _analyse_behaviour_keyword(
            "I'm worried about losing my savings progress",
            memory,
            behaviour_db,
        )

        assert result["detected_principle_id"] == "loss_aversion"
        assert len(result["intervention_suggestions"]) > 0

    def test_habit_loops_detection(self):
        """Test that habit loop keywords are detected."""
        behaviour_db = get_test_behaviour_db()
        memory = UserMemory(user_id="test_user")

        result = _analyse_behaviour_keyword(
            "Every time I get stressed, I automatically start shopping online",
            memory,
            behaviour_db,
        )

        assert result["detected_principle_id"] == "habit_loops"
        assert "every time" in result["triggers_matched"] or "automatic" in result["triggers_matched"]

    def test_no_match_returns_generic(self):
        """Test that no keyword match returns generic guidance."""
        behaviour_db = get_test_behaviour_db()
        memory = UserMemory(user_id="test_user")

        result = _analyse_behaviour_keyword(
            "Hello, how are you?",
            memory,
            behaviour_db,
        )

        assert result["detected_principle_id"] is None
        assert len(result["intervention_suggestions"]) > 0
        assert result["triggers_matched"] == []


class TestLLMIntegration:
    """Tests for LLM-based behaviour analysis."""

    def test_memory_context_building(self):
        """Test that memory context is properly formatted."""
        memory = UserMemory(user_id="test_user")
        memory.goals = [{"description": "Save more money"}]
        memory.streaks = {"savings": {"current": 5, "best": 10}}
        memory.struggles = [{"description": "Impulse buying", "count": 3}]

        context = _build_memory_context(memory)

        assert "Goals: Save more money" in context
        assert "Streaks: 1/1 active" in context
        assert "Recorded struggles: 1" in context

    def test_memory_context_empty(self):
        """Test memory context with no data."""
        memory = UserMemory(user_id="test_user")

        context = _build_memory_context(memory)

        assert "No prior context available" in context

    @patch("src.llm_client.Client")
    @patch("src.llm_client.get_api_key")
    def test_llm_analysis_success(self, mock_get_api_key, mock_client_class):
        """Test successful LLM analysis."""
        # Mock API key
        mock_get_api_key.return_value = "test_api_key"

        # Mock the LLM response
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Create mock response with function call
        mock_function_call = Mock()
        mock_function_call.args = {
            "principle_id": "friction_increase",
            "reason": "User mentions easy access to food delivery",
            "intervention_suggestions": [
                "Delete food delivery apps",
                "Remove saved payment info",
            ],
            "triggers_matched": ["food delivery", "stressed"],
        }

        mock_part = Mock()
        mock_part.function_call = mock_function_call

        mock_content = Mock()
        mock_content.parts = [mock_part]

        mock_candidate = Mock()
        mock_candidate.content = mock_content

        mock_response = Mock()
        mock_response.candidates = [mock_candidate]

        mock_client.models.generate_content.return_value = mock_response

        # Test the function
        behaviour_db = get_test_behaviour_db()
        memory = UserMemory(user_id="test_user")

        result = analyse_behaviour_with_llm(
            "I keep ordering food delivery",
            memory,
            behaviour_db,
        )

        assert result is not None
        assert result["detected_principle_id"] == "friction_increase"
        assert len(result["intervention_suggestions"]) == 2
        assert "food delivery" in result["triggers_matched"]

    @patch("src.llm_client.Client")
    @patch("src.llm_client.get_api_key")
    def test_llm_analysis_failure_returns_none(self, mock_get_api_key, mock_client_class):
        """Test that LLM failure returns None."""
        # Mock API key
        mock_get_api_key.return_value = "test_api_key"

        # Mock client to raise exception
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.models.generate_content.side_effect = Exception("API Error")

        behaviour_db = get_test_behaviour_db()
        memory = UserMemory(user_id="test_user")

        result = analyse_behaviour_with_llm(
            "I keep ordering food delivery",
            memory,
            behaviour_db,
        )

        assert result is None


class TestAnalyseBehaviourIntegration:
    """Tests for the main analyse_behaviour function with LLM + fallback."""

    @patch("src.behaviour_engine.analyse_behaviour_with_llm")
    def test_uses_llm_when_available(self, mock_llm_analysis):
        """Test that LLM is used as primary method."""
        # Mock successful LLM response
        mock_llm_analysis.return_value = {
            "detected_principle_id": "friction_increase",
            "reason": "LLM-detected reason",
            "intervention_suggestions": ["LLM suggestion"],
            "triggers_matched": ["food delivery"],
        }

        behaviour_db = get_test_behaviour_db()
        memory = UserMemory(user_id="test_user")

        result = analyse_behaviour(
            "I keep ordering food delivery",
            memory,
            behaviour_db,
        )

        # Verify LLM was called
        mock_llm_analysis.assert_called_once()

        # Verify result is from LLM
        assert result["reason"] == "LLM-detected reason"
        assert result["intervention_suggestions"] == ["LLM suggestion"]

    @patch("src.behaviour_engine.analyse_behaviour_with_llm")
    def test_falls_back_to_keywords_when_llm_fails(self, mock_llm_analysis):
        """Test that keyword analysis is used when LLM fails."""
        # Mock LLM failure
        mock_llm_analysis.return_value = None

        behaviour_db = get_test_behaviour_db()
        memory = UserMemory(user_id="test_user")

        result = analyse_behaviour(
            "I keep ordering food delivery",
            memory,
            behaviour_db,
        )

        # Verify LLM was called
        mock_llm_analysis.assert_called_once()

        # Verify result is from keyword fallback
        assert result["detected_principle_id"] == "friction_increase"
        assert "delivery" in result["triggers_matched"] or "food delivery" in result["triggers_matched"]
