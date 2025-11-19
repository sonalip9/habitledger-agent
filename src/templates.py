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


def get_weekly_review_template() -> str:
    """
    Get a weekly review template for reflecting on progress.

    This template guides users through a comprehensive weekly reflection,
    helping them identify patterns, biases, struggles, and set focus areas
    for the coming week.

    Returns:
        str: A formatted weekly review script covering the past week's
             patterns, biases, struggles, and next week's focus.

    Example:
        >>> template = get_weekly_review_template()
        >>> print(template)
        📅 Weekly Review
        ...
    """
    template = """
📅 **Weekly Review**

Time to look back at your week and plan ahead!

**Part 1: This Week's Summary**

1. **Wins:** What money habits did you maintain this week?
   - Example: "I avoided food delivery 5 days" or "I saved ₹2000"

2. **Struggles:** What financial challenges did you face?
   - Example: "I overspent on weekend outings" or "I forgot to track expenses"

3. **Patterns:** Did you notice any recurring triggers or situations?
   - Example: "I always spend more on Fridays" or "Stress leads to shopping"

**Part 2: Behavioural Insights**

4. **Biases Detected:** Which behavioural patterns showed up?
   - Loss aversion? Habit loops? Lack of friction?
   - How did they affect your decisions?

5. **What Worked:** Which strategies or interventions helped?
   - Example: "Deleting food apps made a difference"

**Part 3: Next Week's Focus**

6. **One Small Goal:** What's ONE specific habit to work on next week?
   - Make it tiny and specific (e.g., "Save ₹100 daily")

7. **Accountability:** How will you track this goal?
   - Daily check-ins? Streak counter? Accountability partner?

💬 Share your reflections, and I'll help you identify patterns
   and set up a strong plan for next week!
"""
    return template.strip()
