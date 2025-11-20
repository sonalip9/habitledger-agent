"""
ADK integration package for HabitLedger.

This package provides the Google ADK (Agent Development Kit) integration
for HabitLedger, enabling the behavioural money coach to run as an LLM-powered
agent with custom tools and session management.
"""

from .agent import root_agent

__all__ = ["root_agent"]
