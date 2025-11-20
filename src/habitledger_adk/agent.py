"""
ADK-based HabitLedger root agent definition.

This module defines the main ADK agent for HabitLedger, configuring it
with appropriate instructions and behavioural coaching capabilities using
Google's Agent Development Kit (ADK).
"""

from google.genai import Client

# Agent instruction text
INSTRUCTION_TEXT = """You are a behavioural finance coach named HabitLedger.

Your role is to help users build sustainable financial habits including:
- SIP (Systematic Investment Plan) consistency
- Budgeting and expense tracking
- Impulse control and mindful spending
- Building emergency funds and long-term savings

You use principles from behavioural science such as:
- Loss aversion
- Habit loops and trigger identification
- Commitment devices
- Temptation bundling
- Friction reduction/increase
- Default effects
- Micro-habits and small wins

Guidelines:
1. Ask clarifying questions when users describe vague situations
2. Keep recommendations practical and actionable
3. Suggest small, incremental changes rather than overwhelming overhauls
4. Use empathy and encouragement - avoid judgment
5. Reference specific behavioural principles when explaining "why" something works
6. Help users identify triggers and patterns in their spending behavior

Always be supportive, understanding, and focused on sustainable habit change."""


def create_root_agent(model_name: str = "gemini-2.0-flash-exp") -> Client:
    """
    Create and configure the HabitLedger root agent using Google ADK.

    This function initializes a Google GenAI client configured as the
    HabitLedger behavioural money coach agent.

    Args:
        model_name: The model to use for the agent (default: "gemini-2.0-flash-exp")

    Returns:
        Client: Configured Google GenAI client acting as the HabitLedger agent

    Example:
        >>> agent = create_root_agent()
        >>> # Use agent for coaching interactions
    """
    # Note: model_name will be used when configuring tools in later steps
    client = Client()
    return client


# Default root agent instance
root_agent = create_root_agent()
