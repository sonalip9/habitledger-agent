"""
Session management utilities for ADK.

This module provides utilities for creating session services using
Google ADK's InMemorySessionService.
"""

import logging

from google.adk.sessions import InMemorySessionService

logger = logging.getLogger(__name__)


def create_session_service() -> InMemorySessionService:
    """
    Create an InMemorySessionService for session management.

    This function creates a simple in-memory session service using
    Google ADK's native InMemorySessionService. Session state persists
    within the session object during the application lifetime but is
    not persisted across restarts.

    Returns:
        InMemorySessionService: Initialized in-memory session service

    Example:
        >>> service = create_session_service()
        >>> session = service.create_session_sync(
        ...     app_name="habitledger",
        ...     user_id="user123"
        ... )
    """
    logger.info("Creating InMemorySessionService")
    return InMemorySessionService()
