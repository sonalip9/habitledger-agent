"""
ADK integration package for HabitLedger.

This package provides the Google ADK (Agent Development Kit) integration
for HabitLedger, enabling the behavioural money coach to run as an LLM-powered
agent with custom tools and session management.
"""

from .agent import create_root_agent, habitledger_coach_tool
from .runner import run_cli

__all__ = [
    "habitledger_coach_tool",
    "run_cli",
    "create_root_agent",
]
