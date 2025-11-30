"""
Tests for src/memory.py module.

This module tests UserMemory class functionality including:
- Session state scoping with three ADK levels (user:, temp:, empty)
- Data persistence and serialization
- Memory state management
"""

import pytest

from src.memory import UserMemory
from src.models import (
    ConversationRole,
    ConversationTurn,
    Goal,
    Intervention,
    StreakData,
)


class TestScopeValidation:
    """Test scope validation logic."""

    def test_valid_user_scope(self):
        """Test that 'user:' scope is valid."""
        memory = UserMemory(user_id="test")
        session_state = {}
        # Should not raise
        memory.save_to_session_state(session_state, scope="user:")
        assert "user:memory" in session_state

    def test_valid_temp_scope(self):
        """Test that 'temp:' scope is valid."""
        memory = UserMemory(user_id="test")
        session_state = {}
        # Should not raise
        memory.save_to_session_state(session_state, scope="temp:")
        assert "temp:memory" in session_state

    def test_valid_empty_scope(self):
        """Test that empty string scope is valid."""
        memory = UserMemory(user_id="test")
        session_state = {}
        # Should not raise
        memory.save_to_session_state(session_state, scope="")
        assert "memory" in session_state

    def test_invalid_scope_raises_error(self):
        """Test that invalid scope raises ValueError."""
        memory = UserMemory(user_id="test")
        session_state = {}

        with pytest.raises(ValueError, match="Invalid scope"):
            memory.save_to_session_state(session_state, scope="invalid:")  # type: ignore

    def test_invalid_scope_on_load_raises_error(self):
        """Test that invalid scope on load raises ValueError."""
        session_state = {}

        with pytest.raises(ValueError, match="Invalid scope"):
            UserMemory.load_from_session_state(session_state, scope="bad_scope")  # type: ignore


class TestUserScopePersistence:
    """Test 'user:' scope for cross-session persistence."""

    def test_save_with_user_scope(self):
        """Test saving memory with 'user:' scope."""
        memory = UserMemory(user_id="user123")
        memory.goals = [Goal(description="Save ₹10000", target="₹10000")]
        session_state = {}

        memory.save_to_session_state(session_state, scope="user:")

        assert "user:memory" in session_state
        assert session_state["user:memory"]["user_id"] == "user123"
        assert len(session_state["user:memory"]["goals"]) == 1

    def test_load_with_user_scope(self):
        """Test loading memory with 'user:' scope."""
        session_state = {
            "user:memory": {
                "user_id": "user123",
                "goals": [{"description": "Save ₹10000", "target": "₹10000"}],
                "streaks": {},
                "struggles": [],
                "interventions": [],
                "intervention_feedback": {},
                "behaviour_patterns": {},
                "conversation_history": [],
                "user_profile": {},
            }
        }

        memory = UserMemory.load_from_session_state(session_state, scope="user:")

        assert memory is not None
        assert memory.user_id == "user123"
        assert len(memory.goals) == 1
        assert memory.goals[0].description == "Save ₹10000"

    def test_user_scope_persists_across_mock_sessions(self):
        """Test that 'user:' scoped data persists across sessions."""
        # Session 1: Create and save
        session_state_1 = {}
        memory_1 = UserMemory(user_id="user123")
        memory_1.goals = [Goal(description="Save money", target="₹5000")]
        memory_1.save_to_session_state(session_state_1, scope="user:")

        # Simulate session end and new session start
        # In real ADK, 'user:' scoped data persists
        session_state_2 = {"user:memory": session_state_1["user:memory"]}

        # Session 2: Load existing data
        memory_2 = UserMemory.load_from_session_state(session_state_2, scope="user:")

        assert memory_2 is not None
        assert memory_2.user_id == "user123"
        assert len(memory_2.goals) == 1
        assert memory_2.goals[0].description == "Save money"

    def test_user_scope_default_parameter(self):
        """Test that 'user:' is the default scope."""
        memory = UserMemory(user_id="test")
        memory.goals = [Goal(description="Test goal", target="₹1000")]
        session_state = {}

        # Don't specify scope - should default to 'user:'
        memory.save_to_session_state(session_state)

        assert "user:memory" in session_state
        assert session_state["user:memory"]["user_id"] == "test"


class TestTempScopeTransient:
    """Test 'temp:' scope for temporary/transient data."""

    def test_save_with_temp_scope(self):
        """Test saving memory with 'temp:' scope."""
        memory = UserMemory(user_id="user123")
        memory.interventions = [
            Intervention(
                date="2024-01-01T00:00:00",
                intervention_type="test",
                description="Try budgeting app",
            )
        ]
        session_state = {}

        memory.save_to_session_state(session_state, scope="temp:")

        assert "temp:memory" in session_state
        assert session_state["temp:memory"]["user_id"] == "user123"
        assert len(session_state["temp:memory"]["interventions"]) == 1

    def test_load_with_temp_scope(self):
        """Test loading memory with 'temp:' scope."""
        session_state = {
            "temp:memory": {
                "user_id": "user123",
                "goals": [],
                "streaks": {},
                "struggles": [],
                "interventions": [
                    {
                        "date": "2024-01-01",
                        "type": "suggestion",
                        "description": "Draft intervention",
                    }
                ],
                "intervention_feedback": {},
                "behaviour_patterns": {},
                "conversation_history": [],
                "user_profile": {},
            }
        }

        memory = UserMemory.load_from_session_state(session_state, scope="temp:")

        assert memory is not None
        assert memory.user_id == "user123"
        assert len(memory.interventions) == 1
        assert memory.interventions[0].description == "Draft intervention"

    def test_temp_scope_not_accessible_after_invocation(self):
        """Test that 'temp:' scoped data is not accessible after invocation."""
        # During invocation: save to temp
        session_state_during = {}
        memory = UserMemory(user_id="user123")
        memory.interventions = [
            Intervention(
                date="2024-01-01",
                intervention_type="suggestion",
                description="Working memory data",
            )
        ]
        memory.save_to_session_state(session_state_during, scope="temp:")

        # After invocation: temp data is discarded (simulate ADK behavior)
        session_state_after = {}  # ADK clears 'temp:' prefixed data

        loaded_memory = UserMemory.load_from_session_state(
            session_state_after, scope="temp:"
        )

        assert loaded_memory is None

    def test_temp_scope_separate_from_user_scope(self):
        """Test that 'temp:' and 'user:' scopes are independent."""
        session_state = {}

        # Save to both scopes
        memory_user = UserMemory(user_id="user123")
        memory_user.goals = [Goal(description="Long-term goal", target="₹10000")]
        memory_user.save_to_session_state(session_state, scope="user:")

        memory_temp = UserMemory(user_id="user123")
        memory_temp.interventions = [
            Intervention(
                date="2024-01-01",
                intervention_type="calculation",
                description="Temporary calculation",
            )
        ]
        memory_temp.save_to_session_state(session_state, scope="temp:")

        # Both should exist independently
        assert "user:memory" in session_state
        assert "temp:memory" in session_state
        assert len(session_state["user:memory"]["goals"]) == 1
        assert len(session_state["temp:memory"]["interventions"]) == 1


class TestSessionScopeOnly:
    """Test empty string scope for session-only persistence."""

    def test_save_with_session_scope(self):
        """Test saving memory with session-only scope."""
        memory = UserMemory(user_id="user123")
        memory.conversation_history = [
            ConversationTurn(
                role=ConversationRole.USER,
                content="Hello",
                timestamp="2024-01-01T00:00:00",
            )
        ]
        session_state = {}

        memory.save_to_session_state(session_state, scope="")

        assert "memory" in session_state
        assert "user:memory" not in session_state
        assert "temp:memory" not in session_state
        assert session_state["memory"]["user_id"] == "user123"

    def test_load_with_session_scope(self):
        """Test loading memory with session-only scope."""
        session_state = {
            "memory": {
                "user_id": "user123",
                "goals": [],
                "streaks": {},
                "struggles": [],
                "interventions": [],
                "intervention_feedback": {},
                "behaviour_patterns": {},
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Session context",
                        "timestamp": "2024-01-01T00:00:00",
                    }
                ],
                "user_profile": {},
            }
        }

        memory = UserMemory.load_from_session_state(session_state, scope="")

        assert memory is not None
        assert memory.user_id == "user123"
        assert len(memory.conversation_history) == 1

    def test_session_scope_discarded_after_session_ends(self):
        """Test that session-scoped data doesn't persist across sessions."""
        # Session 1: Save session-only data
        session_state_1 = {}
        memory_1 = UserMemory(user_id="user123")
        memory_1.conversation_history = [
            ConversationTurn(
                role=ConversationRole.USER,
                content="Session 1",
                timestamp="2024-01-01T00:00:00",
            )
        ]
        memory_1.save_to_session_state(session_state_1, scope="")

        # Session 2: New session, no session-scoped data
        session_state_2 = {}  # ADK creates fresh state for new session

        loaded_memory = UserMemory.load_from_session_state(session_state_2, scope="")

        assert loaded_memory is None

    def test_session_scope_separate_from_other_scopes(self):
        """Test that session scope is independent from user and temp scopes."""
        session_state = {}

        # Save to all three scopes
        memory_user = UserMemory(user_id="user123")
        memory_user.goals = [Goal(description="User scope", target="₹10000")]
        memory_user.save_to_session_state(session_state, scope="user:")

        memory_temp = UserMemory(user_id="user123")
        memory_temp.interventions = [
            Intervention(
                date="2024-01-01",
                intervention_type="temp",
                description="Temp scope",
            )
        ]
        memory_temp.save_to_session_state(session_state, scope="temp:")

        memory_session = UserMemory(user_id="user123")
        from src.models import Struggle

        memory_session.struggles = [
            Struggle(description="Session scope", first_noted="2024-01-01")
        ]
        memory_session.save_to_session_state(session_state, scope="")

        # All three should coexist independently
        assert "user:memory" in session_state
        assert "temp:memory" in session_state
        assert "memory" in session_state
        assert len(session_state["user:memory"]["goals"]) == 1
        assert len(session_state["temp:memory"]["interventions"]) == 1
        assert len(session_state["memory"]["struggles"]) == 1


class TestMixedScopeUsage:
    """Test scenarios with multiple scopes in use."""

    def test_load_from_different_scopes(self):
        """Test loading different data from different scopes."""
        session_state = {
            "user:memory": {
                "user_id": "user123",
                "goals": [{"description": "Long-term goal", "target": "₹10000"}],
                "streaks": {},
                "struggles": [],
                "interventions": [],
                "intervention_feedback": {},
                "behaviour_patterns": {},
                "conversation_history": [],
                "user_profile": {},
            },
            "temp:memory": {
                "user_id": "user123",
                "goals": [],
                "streaks": {},
                "struggles": [],
                "interventions": [
                    {
                        "date": "2024-01-01",
                        "type": "suggestion",
                        "description": "Draft intervention",
                    }
                ],
                "intervention_feedback": {},
                "behaviour_patterns": {},
                "conversation_history": [],
                "user_profile": {},
            },
            "memory": {
                "user_id": "user123",
                "goals": [],
                "streaks": {},
                "struggles": [],
                "interventions": [],
                "intervention_feedback": {},
                "behaviour_patterns": {},
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Current session",
                        "timestamp": "2024-01-01T00:00:00",
                    }
                ],
                "user_profile": {},
            },
        }

        # Load from each scope
        user_memory = UserMemory.load_from_session_state(session_state, scope="user:")
        temp_memory = UserMemory.load_from_session_state(session_state, scope="temp:")
        session_memory = UserMemory.load_from_session_state(session_state, scope="")

        # Verify each loaded correctly
        assert user_memory is not None
        assert len(user_memory.goals) == 1
        assert user_memory.goals[0].description == "Long-term goal"

        assert temp_memory is not None
        assert len(temp_memory.interventions) == 1
        assert temp_memory.interventions[0].description == "Draft intervention"

        assert session_memory is not None
        assert len(session_memory.conversation_history) == 1

    def test_overwrite_in_same_scope(self):
        """Test that saving to same scope overwrites previous data."""
        session_state = {}

        # First save
        memory_1 = UserMemory(user_id="user123")
        memory_1.goals = [Goal(description="First goal", target="₹5000")]
        memory_1.save_to_session_state(session_state, scope="user:")

        # Second save (overwrites)
        memory_2 = UserMemory(user_id="user123")
        memory_2.goals = [Goal(description="Second goal", target="₹10000")]
        memory_2.save_to_session_state(session_state, scope="user:")

        # Load should get second version
        loaded = UserMemory.load_from_session_state(session_state, scope="user:")

        assert loaded is not None
        assert len(loaded.goals) == 1
        assert loaded.goals[0].description == "Second goal"

    def test_scope_isolation_no_cross_contamination(self):
        """Test that data in one scope doesn't affect other scopes."""
        session_state = {}

        # Save to user scope
        memory_user = UserMemory(user_id="user123")
        memory_user.goals = [Goal(description="User goal", target="₹10000")]
        memory_user.save_to_session_state(session_state, scope="user:")

        # Save different data to temp scope
        memory_temp = UserMemory(user_id="user456")  # Different user_id
        memory_temp.interventions = [
            Intervention(
                date="2024-01-01",
                intervention_type="temp",
                description="Temp data",
            )
        ]
        memory_temp.save_to_session_state(session_state, scope="temp:")

        # Load from user scope should not be affected by temp scope
        loaded_user = UserMemory.load_from_session_state(session_state, scope="user:")
        assert loaded_user is not None
        assert loaded_user.user_id == "user123"
        assert len(loaded_user.interventions) == 0  # No contamination

        # Load from temp scope should not be affected by user scope
        loaded_temp = UserMemory.load_from_session_state(session_state, scope="temp:")
        assert loaded_temp is not None
        assert loaded_temp.user_id == "user456"
        assert len(loaded_temp.goals) == 0  # No contamination


class TestLegacyMigration:
    """Test auto-migration of legacy session state without scope prefix."""

    def test_load_migrates_legacy_data(self):
        """Test that loading from 'user:' scope auto-migrates legacy data."""
        # Legacy session state without scope prefix
        session_state = {
            "memory": {
                "user_id": "legacy_user",
                "goals": [{"description": "Legacy goal", "target": "₹5000"}],
                "streaks": {},
                "struggles": [],
                "interventions": [],
                "intervention_feedback": {},
                "behaviour_patterns": {},
                "conversation_history": [],
                "user_profile": {},
            }
        }

        # Load with 'user:' scope should auto-migrate
        memory = UserMemory.load_from_session_state(session_state, scope="user:")

        assert memory is not None
        assert memory.user_id == "legacy_user"
        assert len(memory.goals) == 1
        assert memory.goals[0].description == "Legacy goal"

    def test_migration_prefers_scoped_data_over_legacy(self):
        """Test that scoped data takes precedence over legacy data."""
        session_state = {
            "user:memory": {
                "user_id": "new_user",
                "goals": [{"description": "New goal", "target": "₹10000"}],
                "streaks": {},
                "struggles": [],
                "interventions": [],
                "intervention_feedback": {},
                "behaviour_patterns": {},
                "conversation_history": [],
                "user_profile": {},
            },
            "memory": {  # Legacy data
                "user_id": "old_user",
                "goals": [{"description": "Old goal", "target": "₹5000"}],
                "streaks": {},
                "struggles": [],
                "interventions": [],
                "intervention_feedback": {},
                "behaviour_patterns": {},
                "conversation_history": [],
                "user_profile": {},
            },
        }

        # Should load new scoped data, not legacy
        memory = UserMemory.load_from_session_state(session_state, scope="user:")

        assert memory is not None
        assert memory.user_id == "new_user"
        assert memory.goals[0].description == "New goal"

    def test_no_migration_for_temp_or_session_scopes(self):
        """Test that auto-migration only happens for 'user:' scope."""
        # Legacy data without scope prefix
        session_state = {
            "memory": {
                "user_id": "test_user",
                "goals": [],
                "streaks": {},
                "struggles": [],
                "interventions": [],
                "intervention_feedback": {},
                "behaviour_patterns": {},
                "conversation_history": [],
                "user_profile": {},
            }
        }

        # Loading with 'temp:' scope should NOT migrate legacy data
        temp_memory = UserMemory.load_from_session_state(session_state, scope="temp:")
        assert temp_memory is None

        # Loading with '' scope should load from 'memory' key (which exists)
        session_memory = UserMemory.load_from_session_state(session_state, scope="")
        assert session_memory is not None
        assert session_memory.user_id == "test_user"


class TestComplexScenarios:
    """Test complex real-world scenarios with session scoping."""

    def test_typical_agent_workflow(self):
        """Test typical agent workflow with multiple scope types."""
        session_state = {}

        # 1. Load or create user memory (cross-session persistence)
        user_memory = UserMemory(user_id="user123")
        user_memory.goals = [Goal(description="Save ₹10000", target="₹10000")]
        user_memory.streaks = {
            "no_delivery": StreakData(current=5, best=10, last_updated="2024-01-01")
        }
        user_memory.save_to_session_state(session_state, scope="user:")

        # 2. Create temporary working memory for current operation
        temp_memory = UserMemory(user_id="user123")
        temp_memory.interventions = [
            Intervention(
                date="2024-01-01",
                intervention_type="draft",
                description="Draft: Try budgeting",
            )
        ]
        temp_memory.save_to_session_state(session_state, scope="temp:")

        # 3. Track session-specific conversation
        session_memory = UserMemory(user_id="user123")
        session_memory.conversation_history = [
            ConversationTurn(
                role=ConversationRole.USER,
                content="I need help",
                timestamp="2024-01-01T00:00:00",
            )
        ]
        session_memory.save_to_session_state(session_state, scope="")

        # Verify all data exists in correct scopes
        assert "user:memory" in session_state
        assert "temp:memory" in session_state
        assert "memory" in session_state

        # Load and verify each scope
        loaded_user = UserMemory.load_from_session_state(session_state, scope="user:")
        assert loaded_user is not None
        assert len(loaded_user.goals) == 1
        assert len(loaded_user.streaks) == 1

        loaded_temp = UserMemory.load_from_session_state(session_state, scope="temp:")
        assert loaded_temp is not None
        assert len(loaded_temp.interventions) == 1

        loaded_session = UserMemory.load_from_session_state(session_state, scope="")
        assert loaded_session is not None
        assert len(loaded_session.conversation_history) == 1

    def test_memory_not_found_returns_none(self):
        """Test that loading from empty session state returns None."""
        session_state = {}

        user_memory = UserMemory.load_from_session_state(session_state, scope="user:")
        temp_memory = UserMemory.load_from_session_state(session_state, scope="temp:")
        session_memory = UserMemory.load_from_session_state(session_state, scope="")

        assert user_memory is None
        assert temp_memory is None
        assert session_memory is None
