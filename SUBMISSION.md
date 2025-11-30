# HabitLedger: Your Personal Behavioral Money Coach

**Competition:** Agents Intensive – Capstone Project (Kaggle)
**Track:** Concierge Agents
**Team:** Solo (Sonali Parekh)
**Repository:** <https://github.com/sonalip9/habitledger-agent>
**Demo:** `notebooks/demo.ipynb`

---

## Problem Statement

Most people know the fundamentals of personal finance—save regularly, avoid impulse purchases, stick to a budget. Yet behavioral patterns consistently undermine financial intentions:

- SIPs get skipped despite best intentions
- "Just this once" food delivery becomes a daily habit
- Budgets are created but never maintained
- Emotional triggers (stress, boredom, FOMO) override rational planning

Traditional finance apps track transactions and visualize spending patterns, but they **fundamentally fail to change behavior**. They show *what* happened without explaining *why* users fall off track or providing timely, personalized interventions.

**The core challenge is behavioral, not analytical.** Sustainable behavior change requires ongoing coaching, contextual memory, and adaptive interventions—capabilities that static tracking apps cannot deliver. Users need a coach who remembers their struggles, recognizes patterns, and provides science-backed guidance precisely when habits are formed or broken.

---

## Why Agents?

Effective behavioral coaching demands capabilities that only agent architectures can deliver:

**1. Stateful Multi-Turn Interaction** - Users need daily check-ins and weekly reflections, not one-time advice. Agents maintain conversational context across sessions, building rapport over time while remembering what worked previously.

**2. Contextual Memory** - A behavioral coach must remember goals, struggles, streak milestones, and emotional triggers. Agents inject this context into every interaction, adapting interventions based on historical effectiveness.

**3. Autonomous Tool Use** - The system must dynamically select behavioral principles (loss aversion, habit loops, friction reduction) and retrieve appropriate interventions. This requires LLM reasoning combined with structured knowledge retrieval—not hardcoded rules.

**4. Adaptive Decision Making** - Agents autonomously decide when to call tools, when to ask clarifying questions, and when to update user state. The coaching flow emerges from reasoning, not fixed scripts.

**5. Human-Centered Flexibility** - Personal finance situations are nuanced and emotional. Agents parse free-text, extract behavioral signals, and respond with empathy that rule-based systems cannot match.

**Traditional chatbots fail here.** They lack memory, cannot reason about which behavioral principle applies, and follow fixed conversation paths. An agent architecture—with LLM reasoning, tools, memory, and orchestration—is the only viable solution for adaptive behavioral coaching.

---

## What I Created

HabitLedger is a **multi-agent behavioral finance coach** built with Google ADK, Gemini models, and custom behavioral science tools.

### System Architecture

```txt
User Input → Coach Agent (Root Orchestrator)
                ├─→ Behavior Analysis (LLM-powered classifier)
                ├─→ behaviour_db_tool (10-principle knowledge base)
                ├─→ Memory Bank (goals, streaks, struggles)
                └─→ Personalized coaching response
```

### Core Components

**Coach Agent** - Root orchestrator built with ADK's `LlmAgent`. Integrates memory into every decision, calls behavior analysis autonomously, and generates empathetic responses with function calling capabilities.

**Behavior Analysis Agent** - LLM-powered classifier that identifies behavioral principles (loss aversion, habit loops, present bias, etc.) and recommends micro-interventions. Includes keyword fallback for reliability.

**Custom Tools** - `behaviour_db_tool` (ADK FunctionTool) retrieves interventions from a 10-principle knowledge base. Each principle contains 3-5 evidence-based micro-habits grounded in behavioral science.

**Memory & Sessions** - JSON-persisted user profiles (goals, streaks, struggles) + ADK InMemorySessionService for conversation context. Memory injection enables truly personalized, context-aware coaching.

**Observability** - Structured logging captures every principle detection, intervention selection, tool call latency, and session state change. Enables debugging, evaluation, and transparency.

### Competition Features Demonstrated

✅ **LLM-powered agents** (Gemini for reasoning/generation)
✅ **Multi-agent system** (Coach + Behavior Analysis agents)
✅ **Custom tools** (`behaviour_db_tool` as ADK FunctionTool)
✅ **Sessions & Memory** (InMemorySessionService + JSON persistence)
✅ **Observability** (Structured logging with 10+ event types)
✅ **Agent evaluation** (20-scenario test suite with metrics)

**Total: 6/6 required features** (minimum 3 required ✓)

---

## Demo

**Interactive Jupyter Notebook:** `notebooks/demo.ipynb` includes full setup, single-interaction trace, and 20-scenario evaluation suite covering missed SIPs, emotional spending, budget drift, and impulse purchases.

### Live Example

**User:** "I keep skipping my SIP. I tell myself I'll double it next month but never do."

**Agent Processing:**

- Detects: Present Bias (prioritizing immediate comfort over future benefits)
- Memory context: User has 30-day SIP consistency goal
- Retrieves interventions: Automation, calendar reminders, commitment devices

**Agent Response:**
> "I hear you—prioritizing today over tomorrow is really common when money feels tight now. This is *present bias*. Let's make it automatic: set up auto-debit for your SIP so the decision happens once, not monthly. Also try marking SIP day with a small reward after (coffee you love). Want help setting that up?"

### Evaluation Results (20 scenarios)

| Category | Detection Accuracy | Intervention Quality |
|----------|-------------------|---------------------|
| Missed SIPs | 100% (5/5) | Highly relevant |
| Emotional spending | 90% (9/10) | Relevant |
| Budget drift | 100% (3/3) | Relevant |
| **Overall** | **95% (19/20)** | **92% relevant+** |

### System Capability Metrics

| Metric | Result | Details |
|--------|--------|----------|
| **Principle Detection Accuracy** | 84.6% (keyword) / 95% (test scenarios) | 11/13 correct in keyword fallback mode |
| **Fallback Reliability** | 100% uptime | Dual-path architecture ensures system always responds |
| **Average Interventions** | 4.8 per scenario | Consistently provides actionable suggestions |
| **Response Latency** | <1ms (keyword) / 500-2000ms (LLM) | Fast fallback when LLM unavailable |

See [docs/EVALUATION_RESULTS.md](docs/EVALUATION_RESULTS.md) for complete test methodology and detailed metrics.

**Quick Start:**

```bash
git clone https://github.com/sonalip9/habitledger-agent.git
cd habitledger-agent && pip install -r requirements.txt
echo "GOOGLE_API_KEY=your_key" > .env
jupyter notebook notebooks/demo.ipynb  # Interactive demo
python -m src.habitledger_adk.runner   # CLI agent
```

---

## The Build

**Technology Stack:**

- **Google ADK**: LlmAgent, FunctionTool, InMemorySessionService, Runner for agent orchestration
- **Gemini Models**: Flash for fast classification, Pro for nuanced coaching generation
- **Python 3.10+** with typed dataclasses for robust domain modeling
- **Custom behavioral knowledge base**: 10 principles × 3-5 interventions, JSON-persisted memory

**Development Process:**

1. **Problem Research** - Studied behavioral economics (Kahneman, Thaler) and habit formation (Clear, Fogg) to identify key principles
2. **Knowledge Base Design** - Curated 10 behavioral principles with evidence-based micro-interventions
3. **Agent Architecture** - Implemented multi-agent system with Coach orchestrator + Behavior Analysis agent
4. **Tool Development** - Created `behaviour_db_tool` as ADK FunctionTool for structured knowledge retrieval
5. **Memory System** - Built JSON-persisted user profiles with goals, streaks, struggles, and intervention feedback
6. **Observability** - Added structured logging with 10+ event types for transparency and debugging
7. **Evaluation** - Designed 20-scenario test suite measuring detection accuracy and intervention relevance

**Key Technical Decisions:**

- **Hybrid LLM + keyword detection**: LLM for nuanced analysis, keywords as reliable fallback
- **Typed domain models**: Dataclasses ensure type safety and clear data contracts
- **Stateful memory injection**: Every agent call receives full user context for personalized responses
- **Comprehensive testing**: 138 tests covering models, services, behavior engine, and orchestration

---

## If I Had More Time

**Production Deployment** - Deploy on Vertex AI Agent Engine with web UI for public access, cloud-based session persistence, and real-time demo capability.

**Planner Agent** - Add secondary agent that converts goals into weekly action plans. Coach Agent executes plans with daily nudges and adaptive scheduling.

**Visual Dashboards** - Streak visualization with progress bars, behavior timeline showing patterns, principle frequency heatmap for self-awareness.

**Transaction Integration** - Privacy-safe local CSV import for automatic pattern detection. Proactive nudges before predicted lapses based on historical spending patterns.

**Mobile Interface** - Telegram/WhatsApp bot for daily check-ins, push-based accountability reminders, and voice input for frictionless logging.

**Multi-language Support** - Extend behavior detection to Spanish, Hindi, and Mandarin for broader accessibility.

---

## Responsible AI

**Not Financial Advice** - HabitLedger provides behavioral coaching only, not investment, tax, or legal guidance.

**Privacy-First** - All memory stored locally by default. No PII shared beyond LLM API calls.

**Transparency** - Structured logs enable users to audit why specific interventions were suggested.

**Safety** - Deterministic keyword fallback prevents hallucinated principles when LLM confidence is low.

---

**Repository:** <https://github.com/sonalip9/habitledger-agent>
**Demo Notebook:** `notebooks/demo.ipynb`
**Documentation:** Comprehensive docs in `README.md` and `docs/` folder
