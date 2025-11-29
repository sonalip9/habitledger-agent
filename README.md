# HabitLedger: A Behavioural Money Coach

HabitLedger is an AI-powered behavioural money coach designed to help users build healthier financial habits.

Instead of recommending specific investments or tax strategies, the agent focuses on **day-to-day financial behaviour** using principles from psychology, behavioural science, and practical habit-building frameworks.

This project is created as part of the **Agents Intensive – Capstone Project on Kaggle**.

---

## ❓ Problem Statement

Most people know *what* they should do with money: save regularly, avoid impulse purchases, stick to a budget. Yet, knowing isn't enough.

**The real struggle is behavioural:**

- You intend to save, but spend on food delivery "just this once" (again)
- You set up a SIP, then stop after a few months
- You create a budget, but never look at it again
- Emotional triggers—stress, boredom, FOMO—override your financial plans

Traditional finance apps focus on tracking transactions or recommending investments. They don't address the **habits, emotions, and biases** that drive day-to-day money decisions.

**The gap:** People need ongoing, personalised support to build and maintain healthy financial habits—not just advice, but *behavioural coaching* that adapts to their struggles over time.

---

## ✅ Solution Overview

**HabitLedger is an AI agent designed to bridge this gap.**

Instead of offering financial advice, HabitLedger acts as a **behavioural money coach** that:

### Why an Agent?

1. **Continuous Interaction**  
   Financial habits aren't built in a single session. HabitLedger engages users over days and weeks through check-ins, reflections, and progress tracking.

2. **Contextual Memory**  
   The agent remembers your goals, past struggles, and progress. It recognizes patterns (like "end-of-month overspending") and adapts interventions accordingly.

3. **Behaviour-Driven Interventions**  
   Using principles from behavioural science (habit loops, loss aversion, friction reduction, commitment devices), HabitLedger suggests small, actionable changes tailored to your situation—not generic tips.

4. **Personalized & Adaptive**  
   The agent analyzes your behaviour, identifies underlying biases, and responds with interventions that match your specific challenges and context.

### What It Does

- **Tracks habits:** Daily check-ins about spending, saving, and budgeting routines
- **Identifies patterns:** Detects recurring struggles and links them to behavioural concepts
- **Suggests micro-interventions:** Small, realistic actions based on proven behaviour change strategies
- **Explains the "why":** Helps you understand the behavioural science behind each suggestion
- **Maintains streaks & progress:** Keeps you motivated with simple tracking and summaries

**Result:** A coach that helps you change *how* you relate to money, one small habit at a time.

### What HabitLedger Helps You Do

- Build consistency with savings or SIPs  
- Reduce impulse spending (for example, food delivery or online shopping)  
- Set and maintain simple budgeting routines  
- Reflect on emotional triggers behind money decisions  
- Track progress over days or weeks with streak tracking
- Receive personalized, actionable interventions (not generic advice)

**Important:** HabitLedger is **not** a financial advisory tool. It does **not** recommend specific stocks, funds, or tax schemes. Its focus is purely on behaviour, routines, and mindset.

---

## 🎯 Features Demonstrated

This project demonstrates the key capabilities expected for the Agents Intensive competition:

✅ **LLM-powered agents** — Gemini models for reasoning and response generation  
✅ **Multi-agent system** — Coach orchestrator + Behavior Analysis agent  
✅ **Custom tools** — `behaviour_db_tool` as ADK FunctionTool for knowledge retrieval  
✅ **Sessions & Memory** — InMemorySessionService + JSON persistence for user state  
✅ **Observability** — Structured logging with 10+ event types for transparency  
✅ **Agent evaluation** — 20-scenario test suite with detection accuracy metrics

**Total: 6/6 required features** (minimum 3 required ✓)

See [Evaluation Results](docs/EVALUATION_RESULTS.md) for detailed metrics and test coverage.

---

## 🧠 Core Concepts

HabitLedger uses ideas from:

- Habit loops (cue → routine → reward)  
- Commitment devices  
- Temptation bundling  
- Loss aversion and risk perception  
- Friction reduction (making good habits easier, bad habits harder)  
- Default effect (helpful defaults)  
- Micro-habits and “2-minute rules”  

These principles are stored in a small internal **behaviour knowledge base**, which the agent uses to:

- Interpret user situations  
- Identify possible behavioural biases  
- Suggest concrete, tailored interventions  

---

## 🏗️ Architecture & Agent Flow

**This is an agent, not just a one-off LLM call.** HabitLedger operates through a continuous interaction loop that maintains state, uses tools, and adapts over time.

### Agent Goal

HabitLedger optimizes for:

- **Improved financial habits** – More consistent savings, reduced impulsive spending
- **Behavior consistency** – Building and maintaining positive routines over days/weeks
- **Self-awareness** – Helping users recognize emotional triggers and biases
- **Sustainable change** – Small, realistic interventions that compound over time

### System Overview

HabitLedger follows a modular architecture with clear separation of concerns:

- **Coach Orchestrator** (`coach.py`) - Central controller managing interaction flow
- **Behaviour Engine** (`behaviour_engine.py`) - Intelligence layer detecting patterns and generating interventions
- **LLM Client** (`llm_client.py`) - Gemini integration with fallback mechanisms
- **Memory Manager** (`memory.py`) - Persistent state across sessions
- **Knowledge Base** (`behaviour_principles.json`) - Behavioral science principles as tool
- **ADK Integration** (`habitledger_adk/`) - Google ADK agent implementation

The agent maintains persistent memory (goals, streaks, struggles, patterns) and adapts interventions based on historical effectiveness. Each interaction updates state, tracks progress, and provides personalized coaching.

### Multi-Step Autonomy

HabitLedger demonstrates true agent autonomy through:

- **Progress Tracking**: Time-based check-ins and follow-ups on interventions
- **Adaptive Recommendations**: Adjusts strategies based on user feedback
- **Pattern Recognition**: Detects recurring triggers and anticipates high-risk situations
- **Multi-Day Journeys**: Breaks goals into trackable micro-habits with celebration of wins

**📚 For detailed architecture diagrams, component interactions, data flow, and type system documentation, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

---

## 🚀 Key Features

### 1. Habit Coaching

Daily check-ins, weekly reflections, and personalised micro-habit suggestions with explanations of *why* they work.

**Example Intervention:**

> **User:** "I keep ordering food delivery when I'm stressed after work."  
> **Agent:** "That sounds like a *habit loop* — stress is your cue, delivery is the routine, and comfort food is the reward. Let's try *substitution*: when you feel the stress cue, try a 5-minute walk before deciding. This breaks the automatic routine while keeping the reward (relaxation)."

### 2. Behaviour Analysis

Detects underlying patterns and links them to behavioural science concepts using LLM-powered analysis with keyword fallback.

**Example Detection:**

```python
# User says: "I want to save but end up spending everything by month end"
AnalysisResult(
    principle_id="present_bias",
    principle_name="Present Bias",
    confidence=0.85,
    interventions=[
        "Set up automatic transfer on salary day",
        "Create a 'spend only' account with limited funds",
        "Use commitment device: tell someone your goal"
    ]
)
```

### 3. Memory & Tracking

Persistent user state with goals, streaks, struggles, and intervention effectiveness tracking.

**Example Memory State:**

```python
{
    "streaks": {
        "no_food_delivery": {"current": 12, "best": 15, "last_updated": "2024-11-17"}
    },
    "intervention_feedback": {
        "friction_increase": {"successes": 8, "failures": 2, "success_rate": 0.80}
    }
}
```

### 4. Observability & Logging

- **Structured logging** with event types, metrics, and decision context
- **Performance monitoring**: Track LLM latency, tool execution time, response generation
- **Decision transparency**: Log every principle detection, confidence score, and intervention selection
- **Session analytics**: Monitor user engagement, streak progress, and intervention effectiveness
- **Error tracking**: Detailed error context with stack traces for debugging
- Compatible with observability tools (ELK, Datadog, Splunk, Prometheus)
- See [docs/OBSERVABILITY.md](docs/OBSERVABILITY.md) for detailed documentation

### 5. Comprehensive Documentation

- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture, component diagrams, data flow, and type system
- **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** - Development setup, workflow, testing guide, and migration instructions
- **[docs/EVALUATION_RESULTS.md](docs/EVALUATION_RESULTS.md)** - Agent evaluation results, test metrics, and coverage analysis
- **[docs/OBSERVABILITY.md](docs/OBSERVABILITY.md)** - Observability implementation, logging patterns, and monitoring

### 6. Demo-Friendly Notebook

- A clean Jupyter notebook for showcasing the agent  
- Sample dialogues and pre-defined scenarios  
- Easy for reviewers to run and understand

---

## 📁 Project Structure

Planned structure (you can adjust as needed):

```text
habitledger/
├── src/
│   ├── coach.py                  # Core agent logic & interaction flow
│   ├── memory.py                 # Simple memory and persistence utilities
│   ├── behaviour_engine.py       # Behaviour classification and interventions
│   ├── config.py                 # Configuration & API key loading
│   └── utils.py                  # Helper utilities (logging, formatting)
│
├── data/
│   └── behaviour_principles.json # Behaviour science & habit strategies
│
├── notebooks/
│   └── demo.ipynb                # Main demo notebook for the agent
│
├── tests/                        # Optional tests for core functions
│
├── requirements.txt
├── README.md
└── .env                          # Environment variables (not committed)
```

---

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/sonalip9/habitledger-agent.git
   cd habitledger-agent
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv

   # macOS / Linux
   source .venv/bin/activate

   # Windows
   .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:

   ```text
   # Required: Google API key for LLM-based analysis
   GOOGLE_API_KEY=your_api_key_here
   
   # Optional: Set the model to use (default: gemini-1.5-flash)
   # gemini-1.5-flash is recommended for better quota management
   GOOGLE_ADK_MODEL=gemini-1.5-flash
   
   # Optional: Rate limiting between LLM calls (default: 1.0 seconds)
   # Increase this if you're hitting quota limits on free tier
   LLM_MIN_CALL_INTERVAL=1.0
   
   # Optional: Set logging level (default: INFO)
   LOG_LEVEL=INFO
   
   # Optional: Enable structured logging for observability tools (default: false)
   STRUCTURED_LOGGING=false
   ```

   **Important:** The agent will use LLM-based analysis when `GOOGLE_API_KEY` is set,
   and automatically fall back to keyword-based analysis if the key is missing
   or LLM calls fail (e.g., quota exhaustion).

   📚 **See [docs/QUOTA_MANAGEMENT.md](docs/QUOTA_MANAGEMENT.md) for detailed quota management guidance.**

---

## 🧭 Competition Track & Scoring Mapping

**Track Selected: Concierge Agents**

This track covers agents designed to help individuals manage and improve aspects of their personal lives  
—for example: travel planning, meal prep, shopping automation, habit-building, or other daily routines.

**HabitLedger fits this track perfectly** because it is a behavioural money coach designed to help users:

- build better financial habits,
- reduce impulse spending,
- maintain savings/budget routines,
- and improve everyday financial decision-making.

It behaves like a personalised **financial habit concierge** that guides, nudges, and adapts to the user over time.

---

## 🚀 Running the Agent

HabitLedger can be run in multiple modes:

### 1. ADK Mode (Recommended)

Run the agent with Google ADK (Agent Development Kit) for LLM-powered interactions:

```bash
# Set up environment
export GOOGLE_API_KEY="your_api_key_here"

# Run the ADK CLI
python -m src.habitledger_adk.runner
```

This mode provides:

- LLM-powered conversational interface
- Automatic tool calling to the HabitLedger coaching engine
- Natural language understanding with Gemini models

### 2. Classic Python Mode

Run the deterministic keyword-based coach directly:

```bash
python -m src.coach
```

This mode uses:

- Keyword-based principle detection
- Direct coaching logic without LLM overhead
- Faster responses for testing and development

### 3. Demo Notebook

Explore interactive examples and scenarios:

```bash
jupyter notebook notebooks/demo.ipynb
```

The notebook demonstrates:

- Single interaction examples
- Multiple scenario testing
- Memory state inspection
- Evaluation criteria

---

## 🧪 Evaluation of the Agent

HabitLedger includes a comprehensive formal evaluation suite with **14 tests** covering **13 scenarios** across all **8 behavioral principles**.

### Evaluation Criteria

HabitLedger can be evaluated on:

- **Clarity** – Are the recommendations easy to understand?
- **Relevance** – Do the suggestions match the user's described situation?
- **Behaviour grounding** – Does the agent correctly connect situations to behavioural principles?
- **Actionability** – Are the suggested actions small, realistic, and actionable?
- **Consistency** – Does the agent remember and reuse user goals and struggles within a session?

### Key Metrics (Keyword Fallback Mode)

| Metric | Result | Threshold |
|--------|--------|-----------|
| Detection Accuracy | **84.6%** | ≥40% |
| Average Interventions | **4.8** per scenario | ≥2 |
| Average Response Length | **413** chars | ≥200 |
| Latency | **<1ms** | <2000ms |

### Principle Coverage

All 8 behavioral principles are tested:

- ✅ habit_loops (3 scenarios, 100% accuracy)
- ✅ loss_aversion (2 scenarios, 100% accuracy)
- ✅ friction_increase (2 scenarios, 100% accuracy)
- ✅ friction_reduction (1 scenario, 100% accuracy)
- ✅ commitment_devices (1 scenario, 100% accuracy)
- ⚠️ default_effect (1 scenario, 0% accuracy - keyword limitation)
- ✅ micro_habits (2 scenarios, 50% accuracy)
- ✅ temptation_bundling (1 scenario, 100% accuracy)

### LLM vs Keyword Mode

| Metric | LLM Mode | Keyword Mode |
|--------|----------|--------------|
| Detection Accuracy | 80-95% | 85% |
| Latency | 500-2000ms | <1ms |
| Context Awareness | Full | Basic |

### Running Evaluation Tests

```bash
# Run all 14 evaluation tests
pytest tests/test_evaluation.py -v

# Run expanded evaluation with metrics output
pytest tests/test_evaluation.py::TestExpandedEvaluation -v -s

# Run comparison and benchmark tests
pytest tests/test_evaluation.py::TestModeComparison -v -s
pytest tests/test_evaluation.py::TestLatencyBenchmarks -v -s
```

For full evaluation methodology and results, see [docs/EVALUATION_RESULTS.md](docs/EVALUATION_RESULTS.md).

---

## 📚 Future Enhancements

### UI/UX Improvements

- [ ] Simple web UI using Streamlit or FastAPI  
- [ ] Visualisation of habit streaks and progress  
- [ ] More detailed behaviour taxonomies and interventions  
- [ ] Optional integration with budgeting or expense-tracking tools  
- [ ] Configurable "modes" for different types of users (students, early-career, families)
- [ ] Improve CLI to be more conversational with clear end outputs (reduce loop-like behavior, ensure interventions are surfaced)

### Additional Testing

- [ ] Add performance benchmarks
- [ ] Add mutation testing for test quality validation

### Code Improvements

- [ ] Add async support for LLM calls
- [ ] Implement caching layer for principle lookups
- [ ] Add rate limiting for API calls

### Documentation (Enhancements)

- [ ] Create video walkthrough of architecture
- [ ] Add API reference documentation
- [ ] Create troubleshooting guide

### Architecture Enhancements

#### Multi-Agent System

- [ ] **Create 3 specialized agents** with distinct responsibilities:
  - **Goal-Setting Agent**: Helps users define SMART financial goals, break them into milestones, and establish initial habit plans
  - **Recommendation Agent**: Analyzes user context and suggests personalized interventions (simple targets or lifestyle changes for building habits)
  - **Adherence Agent**: Monitors habit compliance, tracks progress, and provides feedback loop to Recommendation Agent
- [ ] **Feedback Loop**: Adherence data updates Recommendation Agent's understanding of user personality and mindset, enabling recommendations that align with what users find easier to implement
- [ ] **Agent Coordination**: Implement orchestration layer to manage handoffs between agents and maintain consistent state

#### Knowledge Base Improvements

- [ ] **Migrate to embedding-based search**: Replace keyword matching in `behaviour_principles.json` with vector embeddings and semantic search
- [ ] **Implement continuous improvement loop**: Periodically update the knowledge base with validated LLM outputs
- [ ] **Hybrid fallback strategy**: Use embeddings as primary method with JSON fallback when AI services are unavailable
- [ ] **Knowledge base versioning**: Track changes to principles over time and A/B test effectiveness

#### Persistence & State Management

- [ ] **Database-backed sessions**: Replace in-memory sessions with persistent database storage (PostgreSQL, SQLite, or MongoDB)
- [ ] **Session recovery**: Enable users to resume conversations across devices and time periods
- [ ] **Historical analytics**: Store long-term user data for trend analysis and personalized insights
- [ ] **Multi-user support**: Add user authentication and isolation for production deployment

---

## ⚠️ Disclaimer

- This project does **not** provide personalised financial, legal, or tax advice.  
- Behaviour classification may be imperfect or approximate.  
- The agent is not a substitute for therapy, counselling, or professional financial planning.  

---

## 🙌 Acknowledgements

HabitLedger was created as part of the **Google × Kaggle Agents Intensive – Capstone Project** and is inspired by work in behavioural economics, habit formation, and personal finance education.
