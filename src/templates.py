"""
Interaction templates for HabitLedger coach.

This module provides templated prompts and scripts for different types
of interactions with the user, including daily check-ins and weekly reviews.
These templates help maintain consistent, structured conversations with users.
"""


def get_daily_checkin_prompt() -> str:
    """
    Get a daily check-in prompt for the user.

    This prompt guides users through a brief daily reflection on their
    financial habits, temptations, and any obstacles they encountered.

    Returns:
        str: A formatted daily check-in script with questions about habits,
             temptations, and blockers.

    Example:
        >>> prompt = get_daily_checkin_prompt()
        >>> print(prompt)
        🌅 Daily Check-In
        ...
    """
    template = """
🌅 **Daily Check-In**

Let's take a moment to reflect on your financial habits today:

1. **Habits:** Did you stick to your money habits today?
   - Examples: Made a SIP contribution, avoided impulse purchases,
     tracked expenses, stayed within budget

2. **Temptations:** Did you face any spending temptations?
   - Examples: Food delivery apps, online shopping, impulse buys
   - How did you handle them?

3. **Blockers:** What made it hard to stick to your goals today?
   - Examples: Stress, boredom, social pressure, unclear goals

💬 Share your thoughts, and I'll help you build on successes
   or work through challenges!
"""
    return template.strip()
