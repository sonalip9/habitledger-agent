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


def build_sip_habit_plan(
    goal_amount: float | None = None, monthly_sip: float | None = None
) -> str:
    """
    Build a personalized SIP (Systematic Investment Plan) habit plan.

    This function creates a structured plan to help users build consistent
    savings habits through SIPs. It provides actionable steps, behavioural
    nudges, and timing recommendations.

    Args:
        goal_amount: Optional target savings goal amount
        monthly_sip: Optional monthly SIP contribution amount

    Returns:
        str: A formatted SIP habit plan with setup pattern, starting action,
             timing recommendations, and behavioural nudges.

    Example:
        >>> plan = build_sip_habit_plan(goal_amount=100000, monthly_sip=5000)
        >>> print(plan)
        🎯 Your SIP Habit Plan
        ...
    """
    intro = "🎯 **Your SIP Habit Plan**\n\n"

    if goal_amount and monthly_sip:
        intro += (
            f"Goal: Save ₹{goal_amount:,.0f} | Monthly SIP: ₹{monthly_sip:,.0f}\n\n"
        )
    elif monthly_sip:
        intro += f"Monthly SIP: ₹{monthly_sip:,.0f}\n\n"
    elif goal_amount:
        intro += f"Goal: Save ₹{goal_amount:,.0f}\n\n"

    plan = (
        intro
        + """**1. Setup Pattern — Fixed Date Every Month**
   - Pick a specific date (e.g., 5th of every month)
   - Set up auto-debit so it happens without thinking
   - Mark it on your calendar as a recurring event

**2. Start Now Action (Do This Today)**
   - Open your banking/investment app
   - Set up ONE SIP for the smallest comfortable amount
   - Even ₹500/month is a great start — consistency matters more than amount

**3. Tie to Salary Day**
   - Schedule SIP for 2-3 days after your salary credit date
   - This way, money is "moved away" before you can spend it
   - Treat it as the FIRST expense, not leftover savings

**4. Behavioural Nudge — "Pay Yourself First"**
   - Think of your SIP as a non-negotiable bill (like rent or EMI)
   - You wouldn't skip paying your electricity bill — same logic here
   - Automate it so decision-making is removed from the equation

💡 **Tip:** Start small, automate everything, and increase gradually.
   The habit is more important than the amount!
"""
    )
    return plan.strip()


def build_budget_habit_plan() -> str:
    """
    Build a simple monthly budgeting habit plan.

    This function creates a behaviour-focused budgeting framework using
    simple rules of thumb and micro-habits. Emphasizes habit formation
    over precise financial calculations.

    Returns:
        str: A formatted budget habit plan with the 50/30/20 rule,
             weekly review habits, and spending reduction strategies.

    Example:
        >>> plan = build_budget_habit_plan()
        >>> print(plan)
        💰 Your Budget Habit Plan
        ...
    """
    plan = """💰 **Your Budget Habit Plan**

Building a budget isn't about perfection — it's about building awareness
and simple habits that stick.

**1. Use the 50/30/20 Rule of Thumb**
   - 50% on Needs (rent, groceries, utilities, transport)
   - 30% on Wants (entertainment, dining out, hobbies)
   - 20% on Savings & Debt repayment

   Don't obsess over exact percentages — use this as a rough guide
   to understand where your money goes.

**2. Weekly Budget Review Micro-Habit**
   - Pick ONE day per week (e.g., Sunday evening)
   - Spend 10 minutes reviewing last week's expenses
   - Ask: "Where did I overspend? What surprised me?"
   - Write down ONE insight or pattern you noticed

   💡 The goal is awareness, not judgment.

**3. Pick ONE Category to Reduce**
   - Don't try to cut everything at once
   - Choose ONE spending category you want to consciously reduce
   - Examples: food delivery, impulse online shopping, weekend outings
   - Set a specific weekly cap for that category

**4. Make It a Habit, Not a Spreadsheet**
   - Start with simple tracking (even just notes on your phone)
   - Focus on building the HABIT of checking, not perfect accounting
   - Celebrate small wins (e.g., "I stayed under budget 3 days this week!")

💡 **Tip:** Budgets fail when they're too complex. Keep it simple,
   review regularly, and adjust as you learn your patterns.
"""
    return plan.strip()


def build_overspending_guardrails() -> str:
    """
    Build behavioural guardrails to prevent overspending.

    This function provides a set of practical behaviour-change strategies
    to help users avoid impulsive spending. Focuses on creating friction
    for unnecessary purchases and building conscious decision-making habits.

    Returns:
        str: A formatted set of overspending guardrails with the 24-hour pause rule,
             spending caps, and cash-only strategies.

    Example:
        >>> guardrails = build_overspending_guardrails()
        >>> print(guardrails)
        🛡️ Your Overspending Guardrails
        ...
    """
    plan = """🛡️ **Your Overspending Guardrails**

These are behaviour-focused strategies to help you pause, think, and
avoid impulsive spending. No judgment — just smart guardrails.

**1. The 24-Hour Pause Rule**
   - For any non-essential purchase over ₹500, wait 24 hours
   - Add it to a "wish list" instead of buying immediately
   - Revisit tomorrow: Do you still want it? Need it?
   - Most impulse cravings fade within a day

   💡 This creates friction and gives your rational brain time to catch up.

**2. Weekly Spending Cap for High-Risk Categories**
   - Identify YOUR high-risk spending triggers (e.g., food delivery, online shopping)
   - Set a specific weekly cap (e.g., "Max ₹1000 on food delivery this week")
   - Track it daily — awareness alone reduces spending
   - When you hit the cap, STOP until next week

**3. Cash-Only or Prepaid Wallet Trick**
   - For categories you overspend on, switch to CASH ONLY for one week
   - Or load a fixed amount into a prepaid wallet
   - Once it's gone, it's gone — no refills mid-week
   - Physical or finite money creates natural limits

   💡 Digital payments remove friction; adding it back helps control impulses.

**4. Delete or Logout from Temptation Apps**
   - Uninstall shopping/delivery apps from your phone (or at least logout)
   - If you REALLY need something, you'll make the effort to reinstall
   - This 30-second delay often kills the impulse
   - Keep apps you genuinely need; remove ones that trigger mindless spending

**5. Accountability Check-In**
   - Share your spending goal with someone (friend, partner, or even me!)
   - Do a quick daily/weekly check-in: "Did I stick to my guardrails?"
   - External accountability makes a huge difference

💡 **Tip:** Start with ONE guardrail. Master it. Then add another.
   Behaviour change works best in small steps.
"""
    return plan.strip()
