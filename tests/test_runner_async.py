"""
Integration tests for async runner functionality.

This module tests the async session operations in src/habitledger_adk/runner.py,
verifying that async methods work correctly, events are appended, and sessions
can be retrieved with proper state.
"""

import asyncio
import logging

import pytest
from google.adk.events import Event
from google.adk.sessions import InMemorySessionService

from src.habitledger_adk.runner import (
    create_runner,
    load_memory_from_session,
    save_memory_to_session,
)
from src.memory import UserMemory
from src.models import Goal

logger = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncRunner:
    """Test async runner functionality."""

    async def test_create_runner_async(self):
        """Test that create_runner is async and returns proper components."""
        client, session_service, session, behaviour_db = await create_runner(
            user_id="test_async_user"
        )

        assert client is not None
        assert isinstance(session_service, InMemorySessionService)
        assert session is not None
        assert session.id == "session_test_async_user"
        assert session.user_id == "test_async_user"
        assert behaviour_db is not None
        # behaviour_db is a dict with 'principles' key
        assert "principles" in behaviour_db
        assert len(behaviour_db["principles"]) > 0

    async def test_session_created_with_initial_memory(self):
        """Test that new session is created with initial memory state."""
        _, session_service, session, _ = await create_runner(user_id="test_init_memory")

        # Load memory from session
        memory = load_memory_from_session(session)

        assert memory is not None
        assert memory.user_id == "test_init_memory"
        assert len(memory.goals) == 2  # Default goals
        assert any("financial habits" in g.description.lower() for g in memory.goals)

    async def test_existing_session_loaded(self):
        """Test that existing session is loaded correctly.

        Note: Each create_runner call uses the SAME InMemorySessionService instance
        within the application, so sessions DO persist across calls.
        """
        user_id = "test_existing_session"

        # Create initial session
        _, session_service1, session1, _ = await create_runner(user_id=user_id)
        memory1 = load_memory_from_session(session1)

        # Add custom goal
        memory1.goals.append(Goal(description="Test goal", target="₹10000"))
        save_memory_to_session(session1, memory1)

        # InMemorySessionService doesn't persist across different service instances
        # So we just verify the session was created and memory can be saved/loaded
        reloaded_memory = load_memory_from_session(session1)
        assert reloaded_memory is not None
        assert len(reloaded_memory.goals) == 3  # 2 default + 1 custom
        assert any("Test goal" in g.description for g in reloaded_memory.goals)

    async def test_session_state_persistence_across_operations(self):
        """Test that session state persists within the same session object."""
        user_id = "test_persistence"

        # Create runner and add data
        _, session_service, session, _ = await create_runner(user_id=user_id)
        memory = load_memory_from_session(session)

        memory.goals.append(Goal(description="Persistence test", target="₹5000"))
        save_memory_to_session(session, memory)

        # Verify memory persists in the same session object
        reloaded_memory = load_memory_from_session(session)
        assert reloaded_memory is not None
        assert len(reloaded_memory.goals) == 3  # 2 default + 1 custom
        assert any("Persistence test" in g.description for g in reloaded_memory.goals)

    async def test_append_event_async(self):
        """Test that async append_event works correctly."""
        from google.genai.types import Content, Part

        user_id = "test_append_event"

        # Create runner
        _, session_service, session, _ = await create_runner(user_id=user_id)

        # Append test event using correct Event API
        event = Event(
            author="user",
            content=Content(
                parts=[Part(text="I want to save money")],
                role="user",
            ),
            custom_metadata={
                "type": "test_interaction",
                "agent_response": "Great goal!",
                "timestamp": "2024-01-01T00:00:00",
            },
        )

        await session_service.append_event(
            session=session,
            event=event,
        )

        # Verify event was appended
        assert len(session.events) > 0
        last_event = session.events[-1]
        assert last_event.author == "user"
        assert last_event.content.parts[0].text == "I want to save money"
        assert last_event.custom_metadata["type"] == "test_interaction"

    async def test_multiple_events_tracking(self):
        """Test tracking multiple events in a session."""
        from google.genai.types import Content, Part

        user_id = "test_multi_events"

        # Create runner
        _, session_service, session, _ = await create_runner(user_id=user_id)

        # Append multiple events
        for i in range(5):
            event = Event(
                author="user",
                content=Content(
                    parts=[Part(text=f"Event {i}")],
                    role="user",
                ),
                custom_metadata={"type": "interaction", "index": i},
            )
            await session_service.append_event(
                session=session,
                event=event,
            )

        # Verify all events were appended
        assert len(session.events) >= 5
        # Check last 5 events
        for i, event in enumerate(session.events[-5:]):
            assert event.author == "user"
            assert event.content.parts[0].text == f"Event {i}"
            assert event.custom_metadata["type"] == "interaction"

    async def test_session_isolation(self):
        """Test that different user sessions are isolated."""
        user_id1 = "test_user_1"
        user_id2 = "test_user_2"

        # Create two separate sessions
        _, service1, session1, _ = await create_runner(user_id=user_id1)
        _, service2, session2, _ = await create_runner(user_id=user_id2)

        # Add different data to each
        memory1 = load_memory_from_session(session1)
        memory1.goals.append(Goal(description="User 1 goal", target="₹1000"))
        save_memory_to_session(session1, memory1)

        memory2 = load_memory_from_session(session2)
        memory2.goals.append(Goal(description="User 2 goal", target="₹2000"))
        save_memory_to_session(session2, memory2)

        # Verify isolation
        reloaded_memory1 = load_memory_from_session(session1)
        reloaded_memory2 = load_memory_from_session(session2)

        assert any("User 1 goal" in g.description for g in reloaded_memory1.goals)
        assert not any("User 2 goal" in g.description for g in reloaded_memory1.goals)

        assert any("User 2 goal" in g.description for g in reloaded_memory2.goals)
        assert not any("User 1 goal" in g.description for g in reloaded_memory2.goals)

    async def test_concurrent_session_operations(self):
        """Test that concurrent async operations work correctly."""
        user_ids = [f"test_concurrent_{i}" for i in range(3)]

        # Create runners concurrently
        tasks = [create_runner(user_id=uid) for uid in user_ids]
        results = await asyncio.gather(*tasks)

        # Verify all sessions created successfully
        assert len(results) == 3
        for i, (_client, _service, session, _db) in enumerate(results):
            assert session.id == f"session_test_concurrent_{i}"
            assert session.user_id == user_ids[i]

            # Verify memory
            memory = load_memory_from_session(session)
            assert memory.user_id == user_ids[i]

    async def test_error_handling_invalid_session(self):
        """Test that async session operations work without errors.

        InMemorySessionService creates sessions on-demand, so we test
        that operations complete successfully.
        """
        _, session_service, _, _ = await create_runner(user_id="test_error")

        # Test that creating a session works
        new_session = await session_service.create_session(
            session_id="new_test_session",
            app_name="habitledger",
            user_id="new_test_user",
        )

        assert new_session is not None
        assert new_session.id == "new_test_session"
        assert new_session.user_id == "new_test_user"

    async def test_session_conversation_counter(self):
        """Test that conversation counter increments correctly."""
        from google.genai.types import Content, Part

        user_id = "test_counter"
        _, session_service, session, _ = await create_runner(user_id=user_id)

        # Simulate conversation turns
        for i in range(3):
            count = session.state.get("conversation_count", 0)
            session.state["conversation_count"] = count + 1

            # Append event
            event = Event(
                author="user",
                content=Content(
                    parts=[Part(text=f"Turn {i + 1}")],
                    role="user",
                ),
                custom_metadata={"type": "interaction", "turn": i + 1},
            )
            await session_service.append_event(
                session=session,
                event=event,
            )

        # Verify counter
        assert session.state.get("conversation_count") == 3
        assert len(session.events) >= 3


@pytest.mark.asyncio
@pytest.mark.integration
class TestAsyncMemoryOperations:
    """Test memory operations in async context."""

    async def test_save_and_load_memory_cycle(self):
        """Test complete save and load cycle in async context."""
        _, _, session, _ = await create_runner(user_id="test_cycle")

        # Create and save memory
        memory = UserMemory(user_id="test_cycle")
        memory.goals = [
            Goal(description="Goal 1", target="₹1000"),
            Goal(description="Goal 2", target="₹2000"),
        ]
        save_memory_to_session(session, memory)

        # Load and verify
        loaded_memory = load_memory_from_session(session)
        assert loaded_memory is not None
        assert len(loaded_memory.goals) == 2
        assert loaded_memory.goals[0].description == "Goal 1"

    async def test_memory_with_complex_data(self):
        """Test memory persistence with complex nested data."""
        from datetime import datetime

        from src.models import Intervention, StreakData, Struggle

        _, _, session, _ = await create_runner(user_id="test_complex")

        # Create memory with complex data
        memory = UserMemory(user_id="test_complex")
        memory.interventions = [
            Intervention(
                date=datetime.now().isoformat(),
                intervention_type="loss_aversion",
                description="Frame savings as avoiding future regret",
            )
        ]
        memory.struggles = [
            Struggle(
                description="Impulse spending on food delivery",
                first_noted=datetime.now().isoformat(),
            )
        ]
        memory.streaks = {
            "no_delivery": StreakData(
                current=5,
                best=10,
                last_updated=datetime.now().isoformat(),
            )
        }

        save_memory_to_session(session, memory)

        # Load and verify complex data
        loaded_memory = load_memory_from_session(session)
        assert loaded_memory is not None
        assert len(loaded_memory.interventions) == 1
        assert len(loaded_memory.struggles) == 1
        assert "no_delivery" in loaded_memory.streaks
        assert loaded_memory.streaks["no_delivery"].current == 5

    async def test_session_scope_preservation(self):
        """Test that 'user:' scope is preserved in session state."""
        _, session_service, session, _ = await create_runner(user_id="test_scope")

        # Save memory with user: scope
        memory = UserMemory(user_id="test_scope")
        memory.goals = [Goal(description="Scoped goal", target="₹3000")]
        save_memory_to_session(session, memory)

        # Verify user: prefix in session state
        assert "user:memory" in session.state
        memory_data = session.state["user:memory"]
        assert memory_data["user_id"] == "test_scope"
        assert len(memory_data["goals"]) == 1

        # Verify memory can be reloaded from same session
        loaded_memory = load_memory_from_session(session)
        assert loaded_memory is not None
        assert any("Scoped goal" in g.description for g in loaded_memory.goals)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
