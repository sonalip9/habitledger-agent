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

## 🚀 Key Features

### 1. Habit Coaching

- Daily check-ins about spending, saving, and budgeting  
- Weekly reflections on progress and setbacks  
- Personalised micro-habit suggestions  
- Explanations of *why* a habit is likely to work

### 2. Behaviour Analysis

- Detects underlying patterns (for example, “end-of-month overspending”)  
- Links user behaviour to behavioural science concepts  
- Suggests targeted interventions aligned with the detected bias

### 3. Memory & Tracking

- Stores user goals (for example, “save a fixed amount each month”)  
- Tracks simple streaks (days you reported sticking to a habit)  
- Records recurring struggles in free-text form  
- Generates simple summaries of recent behaviour

### 4. Demo-Friendly Notebook

- A clean Jupyter notebook for showcasing the agent  
- Sample dialogues and pre-defined scenarios  
- Easy for reviewers to run and understand

---

## 📁 Project Structure

Planned structure (you can adjust as needed):

.
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

---

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd habitledger
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

   Once `requirements.txt` is created:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:

   ```text
   OPENAI_API_KEY=your_api_key_here
   ```

   Or adapt to the LLM provider you use.

---

## ▶️ Running the Agent

### Option 1: From the Notebook (Recommended for Demo)

1. Open the notebook:

   ```bash
   jupyter notebook notebooks/demo.ipynb
   ```

2. Run all cells in order.  
3. Interact with the agent through the provided input cells.

### Option 2: From the Command Line (Optional)

You can add a simple CLI entry point in `src/coach.py`:

```bash
python src/coach.py
```

This can start a simple text-based chat loop with the coach.

---

## 🧭 Competition Track & Scoring Mapping

### **Track Selected: Concierge Agents**

This track covers agents designed to help individuals manage and improve aspects of their personal lives  
—for example: travel planning, meal prep, shopping automation, habit-building, or other daily routines.

**HabitLedger fits this track perfectly** because it is a behavioural money coach designed to help users:

- build better financial habits,
- reduce impulse spending,
- maintain savings/budget routines,
- and improve everyday financial decision-making.

It behaves like a personalised **financial habit concierge** that guides, nudges, and adapts to the user over time.

---

### 🏆 How HabitLedger Meets the Competition Scoring Criteria

| Criterion | How HabitLedger satisfies it |
|----------|-------------------------------|
| **Problem Relevance** | Addresses the widespread issue of inconsistent financial habits and impulsive spending — a major everyday productivity barrier. |
| **Agentic Design** | Maintains user memory (goals, streaks), uses a behaviour-principles knowledge base as a “tool”, performs multi-turn reasoning and adaptive interactions. |
| **Technical Execution** | Modular Python structure (`coach.py`, `behaviour_engine.py`, `memory.py`), documented code, single-purpose functions, DRY, clean commits. |
| **User Experience & Novelty** | Provides personalised interventions grounded in behavioural science, making the agent feel like a real habit coach rather than a generic chatbot. |
| **Evaluation & Impact** | Includes structured test scenarios (missed SIP, impulsive spend, budgeting challenge) and measures progress via streaks, goal tracking, and behaviour patterns. |

---

### 🎯 Awards Positioning Strategy

- HabitLedger aims for awards in **Concierge Agent excellence** by demonstrating:
  - long-term interaction loops,
  - adaptive behaviour,
  - meaningful improvements to daily life (financial habits),
  - clarity and structure in user guidance.
- The demo notebook presents clear user journeys and behaviour-change processes.
- The storytelling and architecture highlight HabitLedger as a true **agent** — not just an LLM wrapper.

---

## 🧪 Evaluation

HabitLedger can be evaluated on:

- **Clarity** – Are the recommendations easy to understand?  
- **Relevance** – Do the suggestions match the user’s described situation?  
- **Behaviour grounding** – Does the agent correctly connect situations to behavioural principles?  
- **Actionability** – Are the suggested actions small, realistic, and actionable?  
- **Consistency** – Does the agent remember and reuse user goals and struggles within a session?

A small evaluation set of user scenarios and expected behaviours will be documented in the `notebooks/demo.ipynb` notebook.

---

## ⚠️ Limitations

- This project does **not** provide personalised financial, legal, or tax advice.  
- Behaviour classification may be imperfect or approximate.  
- The agent is not a substitute for therapy, counselling, or professional financial planning.  
- Memory is local to the current environment; it does not sync across devices or users.  

---

## 📚 Future Enhancements

Potential improvements:

- Simple web UI using Streamlit or FastAPI  
- Visualisation of habit streaks and progress  
- More detailed behaviour taxonomies and interventions  
- Optional integration with budgeting or expense-tracking tools  
- Configurable “modes” for different types of users (students, early-career, families)

---

## 🙌 Acknowledgements

HabitLedger was created as part of the **Google × Kaggle Agents Intensive – Capstone Project** and is inspired by work in behavioural economics, habit formation, and personal finance education.
