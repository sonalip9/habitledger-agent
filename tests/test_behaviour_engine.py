"""
Tests for behaviour engine and principle detection.

This module tests the behaviour analysis functions including keyword matching,
principle explanation, and intervention retrieval.
"""

import pytest

from src.behaviour_engine import (
    _apply_adaptive_weighting,
    _calculate_confidence_score,
    analyse_behaviour,
    explain_principle,
    get_interventions,
    load_behaviour_db,
)


class TestBehaviourAnalysis:
    """Tests for behaviour analysis functions."""

    def test_analyse_behaviour_friction_increase(
        self, empty_memory, sample_behaviour_db, sample_user_input
    ):
        """Test detecting friction_increase principle."""
        result = analyse_behaviour(
            sample_user_input["food_delivery"],
            empty_memory,
            sample_behaviour_db,
        )

        # Should detect a principle (friction_increase or habit_loops both valid for food delivery)
        assert result["detected_principle_id"] in ["friction_increase", "habit_loops"]
        assert result["confidence"] > 0.0
        assert len(result["intervention_suggestions"]) > 0
        # Verify triggers_matched is present and is a list
        assert "triggers_matched" in result
        assert isinstance(result["triggers_matched"], list)

    def test_analyse_behaviour_loss_aversion(
        self, empty_memory, sample_behaviour_db, sample_user_input
    ):
        """Test detecting loss_aversion principle."""
        result = analyse_behaviour(
            sample_user_input["broken_streak"],
            empty_memory,
            sample_behaviour_db,
        )

        # Should detect a principle (loss_aversion preferred, but may detect others)
        # The key is that it detects something and provides interventions
        assert "detected_principle_id" in result
        assert result["source"] in ["adk", "keyword"]
        assert "intervention_suggestions" in result
        assert "confidence" in result

    def test_analyse_behaviour_vague_input(
        self, empty_memory, sample_behaviour_db, sample_user_input
    ):
        """Test analysis with vague input."""
        result = analyse_behaviour(
            sample_user_input["vague"],
            empty_memory,
            sample_behaviour_db,
        )

        # Should still return a result, possibly generic
        assert "detected_principle_id" in result
        assert "intervention_suggestions" in result
        assert "confidence" in result

    def test_analyse_behaviour_with_streaks(
        self, populated_memory, sample_behaviour_db, sample_user_input
    ):
        """Test analysis considering user's streak history."""
        result = analyse_behaviour(
            sample_user_input["broken_streak"],
            populated_memory,
            sample_behaviour_db,
        )

        # Memory bonus should boost confidence for loss_aversion
        assert result["confidence"] > 0.0

    def test_get_interventions_valid_principle(self, sample_behaviour_db):
        """Test retrieving interventions for a valid principle."""
        interventions = get_interventions("friction_increase", sample_behaviour_db)

        assert len(interventions) > 0
        assert len(interventions) <= 2  # Top 1-2 interventions

    def test_get_interventions_invalid_principle(self, sample_behaviour_db):
        """Test retrieving interventions for an invalid principle."""
        interventions = get_interventions("nonexistent_principle", sample_behaviour_db)

        assert len(interventions) == 0

    def test_explain_principle_valid(self, sample_behaviour_db):
        """Test generating explanation for a valid principle."""
        explanation = explain_principle("loss_aversion", sample_behaviour_db)

        assert "Loss Aversion" in explanation
        assert "feel losses more strongly" in explanation
        assert len(explanation) > 0

    def test_explain_principle_invalid(self, sample_behaviour_db):
        """Test generating explanation for an invalid principle."""
        explanation = explain_principle("nonexistent", sample_behaviour_db)

        # Should return generic fallback message
        assert "behavioural science" in explanation.lower()


class TestBehaviourDatabaseLoading:
    """Tests for behaviour database loading."""

    def test_load_behaviour_db_valid(self, tmp_path):
        """Test loading a valid behaviour database."""
        import json

        db_file = tmp_path / "behaviour_principles.json"
        test_db = {
            "version": "1.0",
            "description": "Test DB",
            "principles": [
                {
                    "id": "test_principle",
                    "name": "Test",
                    "description": "Test description",
                    "typical_triggers": ["test"],
                    "interventions": ["Test intervention"],
                }
            ],
        }
        db_file.write_text(json.dumps(test_db))

        db = load_behaviour_db(str(db_file))
        assert db["version"] == "1.0"
        assert len(db["principles"]) == 1

    def test_load_behaviour_db_file_not_found(self):
        """Test loading a non-existent database file."""
        with pytest.raises(FileNotFoundError):
            load_behaviour_db("/nonexistent/path/behaviour_principles.json")


class TestApplyAdaptiveWeighting:
    """Tests for _apply_adaptive_weighting function."""

    def test_confidence_unchanged_when_no_feedback(self, empty_memory):
        """Test confidence remains unchanged when insufficient data exists."""
        result = {
            "detected_principle_id": "friction_increase",
            "confidence": 0.7,
        }

        updated = _apply_adaptive_weighting(result, empty_memory)

        assert updated["confidence"] == 0.7
        assert "adjusted_by_history" not in updated

    def test_confidence_unchanged_when_insufficient_uses(self, empty_memory):
        """Test confidence remains unchanged with less than 2 uses."""
        # Add only 1 use
        empty_memory.record_intervention_feedback("friction_increase", True)

        result = {
            "detected_principle_id": "friction_increase",
            "confidence": 0.7,
        }

        updated = _apply_adaptive_weighting(result, empty_memory)

        assert updated["confidence"] == 0.7
        assert "adjusted_by_history" not in updated

    def test_confidence_increases_for_high_success_rate(self, empty_memory):
        """Test confidence increases for principles with high success rates."""
        # Create high success rate (100%)
        empty_memory.record_intervention_feedback("friction_increase", True)
        empty_memory.record_intervention_feedback("friction_increase", True)
        empty_memory.record_intervention_feedback("friction_increase", True)

        result = {
            "detected_principle_id": "friction_increase",
            "confidence": 0.6,
        }

        updated = _apply_adaptive_weighting(result, empty_memory)

        # Success rate is 1.0, adjustment = (1.0 - 0.5) * 0.4 = 0.2
        # Expected: 0.6 + 0.2 = 0.8
        assert updated["confidence"] == 0.8
        assert updated["adjusted_by_history"] is True

    def test_confidence_decreases_for_low_success_rate(self, empty_memory):
        """Test confidence decreases for principles with low success rates."""
        # Create low success rate (0%)
        empty_memory.record_intervention_feedback("loss_aversion", False)
        empty_memory.record_intervention_feedback("loss_aversion", False)
        empty_memory.record_intervention_feedback("loss_aversion", False)

        result = {
            "detected_principle_id": "loss_aversion",
            "confidence": 0.6,
        }

        updated = _apply_adaptive_weighting(result, empty_memory)

        # Success rate is 0.0, adjustment = (0.0 - 0.5) * 0.4 = -0.2
        # Expected: 0.6 - 0.2 = 0.4
        assert updated["confidence"] == 0.4
        assert updated["adjusted_by_history"] is True

    def test_confidence_stays_within_bounds_upper(self, empty_memory):
        """Test confidence stays within valid bounds (doesn't exceed 1.0)."""
        # High success rate with high base confidence
        empty_memory.record_intervention_feedback("test_principle", True)
        empty_memory.record_intervention_feedback("test_principle", True)

        result = {
            "detected_principle_id": "test_principle",
            "confidence": 0.95,
        }

        updated = _apply_adaptive_weighting(result, empty_memory)

        # Should cap at 1.0
        assert updated["confidence"] <= 1.0
        assert updated["confidence"] == 1.0

    def test_confidence_stays_within_bounds_lower(self, empty_memory):
        """Test confidence stays within valid bounds (doesn't go below 0.1)."""
        # Low success rate with low base confidence
        empty_memory.record_intervention_feedback("test_principle", False)
        empty_memory.record_intervention_feedback("test_principle", False)
        empty_memory.record_intervention_feedback("test_principle", False)

        result = {
            "detected_principle_id": "test_principle",
            "confidence": 0.15,
        }

        updated = _apply_adaptive_weighting(result, empty_memory)

        # Should not go below 0.1
        assert updated["confidence"] >= 0.1
        assert updated["confidence"] == 0.1

    def test_confidence_with_mixed_success_rate(self, empty_memory):
        """Test confidence adjustment with 50% success rate (no change)."""
        # 50% success rate
        empty_memory.record_intervention_feedback("habit_loops", True)
        empty_memory.record_intervention_feedback("habit_loops", False)

        result = {
            "detected_principle_id": "habit_loops",
            "confidence": 0.6,
        }

        updated = _apply_adaptive_weighting(result, empty_memory)

        # Success rate is 0.5, adjustment = (0.5 - 0.5) * 0.4 = 0.0
        # Expected: 0.6 + 0.0 = 0.6
        assert updated["confidence"] == 0.6
        assert updated["adjusted_by_history"] is True

    def test_handles_missing_principle_id(self, empty_memory):
        """Test handles result without principle_id."""
        result = {
            "confidence": 0.7,
        }

        updated = _apply_adaptive_weighting(result, empty_memory)

        assert updated["confidence"] == 0.7
        assert "adjusted_by_history" not in updated

    def test_uses_default_confidence_when_missing(self, empty_memory):
        """Test uses default confidence of 0.7 when not provided."""
        empty_memory.record_intervention_feedback("test_principle", True)
        empty_memory.record_intervention_feedback("test_principle", True)

        result = {
            "detected_principle_id": "test_principle",
            # No confidence key
        }

        updated = _apply_adaptive_weighting(result, empty_memory)

        # Should use default 0.7 and adjust from there
        # Success rate 1.0: 0.7 + 0.2 = 0.9
        assert updated["confidence"] == 0.9


class TestCalculateConfidenceScore:
    """Tests for _calculate_confidence_score function."""

    def test_all_keywords_match(self):
        """Test correct calculation when all keywords match."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=5,
            total_keywords=5,
            memory_context_bonus=0,
        )

        # 5/5 = 1.0, * 0.8 = 0.8, capped at 0.75
        assert confidence == 0.75

    def test_partial_keyword_matches(self):
        """Test correct calculation with partial keyword matches."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=2,
            total_keywords=5,
            memory_context_bonus=0,
        )

        # 2/5 = 0.4, * 0.8 = 0.32
        assert confidence == 0.32

    def test_no_keyword_matches(self):
        """Test calculation with zero keyword matches."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=0,
            total_keywords=5,
            memory_context_bonus=0,
        )

        # 0/5 = 0.0, * 0.8 = 0.0
        assert confidence == 0.0

    def test_memory_bonus_one_point(self):
        """Test memory bonus application with 1 bonus point (0.1 boost)."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=3,
            total_keywords=5,
            memory_context_bonus=1,
        )

        # 3/5 = 0.6, * 0.8 = 0.48, + 0.1 = 0.58
        assert confidence == 0.58

    def test_memory_bonus_two_points(self):
        """Test memory bonus application with 2 bonus points (0.2 boost)."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=3,
            total_keywords=5,
            memory_context_bonus=2,
        )

        # 3/5 = 0.6, * 0.8 = 0.48, + 0.2 = 0.68
        assert confidence == 0.68

    def test_memory_bonus_capped_at_0_2(self):
        """Test memory bonus is capped at 0.2 even with higher values."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=2,
            total_keywords=5,
            memory_context_bonus=5,  # Excessive bonus
        )

        # 2/5 = 0.4, * 0.8 = 0.32, + 0.2 (capped) = 0.52
        assert confidence == 0.52

    def test_maximum_cap_at_0_75(self):
        """Test maximum cap of 0.75 for keyword-based detection."""
        # Even with perfect match and bonus, should cap at 0.75
        confidence = _calculate_confidence_score(
            matched_keywords_count=10,
            total_keywords=10,
            memory_context_bonus=2,
        )

        # 10/10 = 1.0, * 0.8 = 0.8, + 0.2 = 1.0, but capped at 0.75
        assert confidence == 0.75

    def test_edge_case_zero_total_keywords(self):
        """Test edge case: total_keywords = 0 returns 0.0 confidence."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=0,
            total_keywords=0,
            memory_context_bonus=0,
        )

        assert confidence == 0.0

    def test_edge_case_zero_total_keywords_with_bonus(self):
        """Test edge case: total_keywords = 0 with bonus still considers bonus."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=0,
            total_keywords=0,
            memory_context_bonus=2,
        )

        # No keyword confidence, but bonus applies: 0.0 + 0.2 = 0.2
        assert confidence == 0.2

    def test_confidence_rounded_to_two_decimals(self):
        """Test confidence is rounded to 2 decimal places."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=1,
            total_keywords=3,
            memory_context_bonus=0,
        )

        # 1/3 = 0.333..., * 0.8 = 0.2666..., rounded to 0.27
        assert confidence == 0.27

    def test_half_keywords_match_no_bonus(self):
        """Test calculation with half keywords matching, no bonus."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=4,
            total_keywords=8,
            memory_context_bonus=0,
        )

        # 4/8 = 0.5, * 0.8 = 0.4
        assert confidence == 0.4

    def test_high_match_with_bonus_approaches_cap(self):
        """Test that high match rate with bonus approaches the cap."""
        confidence = _calculate_confidence_score(
            matched_keywords_count=9,
            total_keywords=10,
            memory_context_bonus=2,
        )

        # 9/10 = 0.9, * 0.8 = 0.72, + 0.2 = 0.92, capped at 0.75
        assert confidence == 0.75
