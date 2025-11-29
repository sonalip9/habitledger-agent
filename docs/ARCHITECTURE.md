
# HabitLedger Architecture

This document provides an in-depth architectural overview of the HabitLedger agent system, including system diagrams, data flow, and component interactions.

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagrams](#architecture-diagrams)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Type System](#type-system)

## System Overview

HabitLedger follows a clean, layered architecture with clear separation of concerns:

- **Presentation Layer**: CLI, Jupyter notebooks
- **Application Layer**: Coach orchestrator, response generation
- **Business Logic Layer**: Behaviour analysis, memory services
- **Data Layer**: UserMemory, behaviour database
- **External Services**: Google GenAI (Gemini), ADK framework

## Architecture Diagrams

### High-Level System Architecture

```mermaid
graph TB
    User[User Interface<br/>CLI / Notebook]
    Coach[Coach Orchestrator<br/>coach.py]
    Engine[Behaviour Engine<br/>behaviour_engine.py]
    LLM[LLM Client<br/>llm_client.py]
    Memory[Memory Manager<br/>memory.py]
    Service[Memory Service<br/>memory_service.py]
    DB[(Behaviour DB<br/>JSON)]
    ADK[ADK Agent<br/>habitledger_adk/]
    
    User -->|User Input| Coach
    Coach -->|Analyze| Engine
    Coach -->|Read/Write| Memory
    Coach -->|Optional| ADK
    
    Engine -->|LLM Analysis| LLM
    Engine -->|Query| DB
    
    Service -->|Business Logic| Memory
    
    ADK -->|Tool Calls| Engine
    ADK -->|State| Memory
    
    LLM -->|API Calls| Gemini[Google Gemini API]
    
    Coach -->|Response| User
    
    style Coach fill:#e1f5ff
    style Engine fill:#fff3cd
    style Memory fill:#d4edda
    style ADK fill:#f8d7da
```

### Request Flow Diagram

```mermaid
sequenceDiagram
    actor User
    participant Coach
    participant Engine
    participant LLM
    participant Memory
    participant DB
    
    User->>Coach: User message
    Coach->>Memory: Load user context
    Memory-->>Coach: Goals, streaks, history
    
    Coach->>Engine: Analyze behaviour (message + context)
    
    alt LLM Available
        Engine->>LLM: Request analysis
        LLM->>Gemini: API call
        Gemini-->>LLM: Principle + reasoning
        LLM-->>Engine: Structured result
    else LLM Unavailable
        Engine->>DB: Keyword matching
        DB-->>Engine: Matched principles
    end
    
    Engine-->>Coach: Analysis result (principle + interventions)
    
    Coach->>Coach: Build response
    Coach->>Memory: Record interaction
    
    Coach-->>User: Coaching response
```

### Data Model Architecture

```mermaid
classDiagram
    class UserMemory {
        +user_id: str
        +goals: list~Goal~
        +streaks: dict~str, StreakData~
        +struggles: list~Struggle~
        +interventions: list~Intervention~
        +conversation_history: list~ConversationTurn~
        +intervention_feedback: dict~str, InterventionFeedback~
        +user_profile: UserProfile
        +add_conversation_turn()
        +record_interaction()
        +save_to_file()
        +load_from_file()
    }
    
    class Goal {
        +description: str
        +target: str
        +created_at: str
        +completed: bool
    }
    
    class StreakData {
        +current: int
        +best: int
        +last_updated: str
    }
    
    class Struggle {
        +description: str
        +first_noted: str
        +last_noted: str
        +count: int
    }
    
    class ConversationTurn {
        +role: ConversationRole
        +content: str
        +timestamp: str
        +metadata: dict
    }
    
    class InterventionFeedback {
        +successes: int
        +failures: int
        +total: int
        +success_rate: float
    }
    
    class BehaviourDatabase {
        +version: str
        +description: str
        +principles: list~BehaviouralPrinciple~
        +get_principle_by_id()
    }
    
    class BehaviouralPrinciple {
        +id: str
        +name: str
        +description: str
        +typical_triggers: list~str~
        +interventions: list~str~
    }
    
    UserMemory "1" --> "*" Goal
    UserMemory "1" --> "*" StreakData
    UserMemory "1" --> "*" Struggle
    UserMemory "1" --> "*" ConversationTurn
    UserMemory "1" --> "*" InterventionFeedback
    BehaviourDatabase "1" --> "*" BehaviouralPrinciple
```

### Component Interaction Flow

```mermaid
flowchart TD
    Start([User Input]) --> A[Coach: run_once]
    A --> B[Record user message]
    B --> C[Behaviour Engine: analyse_behaviour]
    
    C --> D{LLM Available?}
    D -->|Yes| E[LLM Client: analyse_behaviour_with_llm]
    D -->|No| F[Keyword-based analysis]
    
    E --> G[Parse LLM response]
    F --> H[Keyword matching]
    
    G --> I{Valid principle?}
    H --> I
    
    I -->|Yes| J[Return AnalysisResult]
    I -->|No| F
    
    J --> K{Confidence > 0.6?}
    K -->|No| L[Generate clarifying questions]
    K -->|Yes| M{Try ADK agent?}
    
    M -->|Yes| N[Call ADK agent]
    M -->|No| O[Build template response]
    
    N --> P{ADK Success?}
    P -->|Yes| Q[Use ADK response]
    P -->|No| O
    
    L --> R[Finalize response]
    Q --> R
    O --> R
    
    R --> S[Update memory]
    S --> T[Record conversation]
    T --> End([Return response])
    
    style Start fill:#e1f5ff
    style End fill:#d4edda
    style E fill:#fff3cd
    style N fill:#f8d7da
```

## Component Details

### Coach (coach.py)

**Responsibility**: Central orchestrator for agent interactions

**Key Functions**:

- `run_once(user_input, memory, behaviour_db)`: Main entry point for processing user input
- `_handle_low_confidence_case()`: Generates clarifying questions for uncertain detections
- `_build_template_response()`: Creates fallback responses without ADK
- `_finalize_response()`: Records responses in memory and returns to user
- `call_adk_agent()`: Optional integration with Google ADK for enhanced responses
- `generate_session_summary()`: Creates progress summaries

**Dependencies**: behaviour_engine, memory, llm_client, models, adk_config, adk_tools

### ADK Config (adk_config.py)

**Responsibility**: Shared ADK configuration to prevent circular dependencies

**Key Content**:

- `INSTRUCTION_TEXT`: System prompt/instruction text for ADK agents
- Shared constant used by both `coach.py` and `habitledger_adk/agent.py`
- Eliminates circular import between coach and ADK agent modules

**Purpose**: This module was created as part of the "Extract Shared Components" pattern to resolve circular dependencies between the coach orchestrator and ADK agent implementation.

### ADK Tools (adk_tools.py)

**Responsibility**: Shared ADK tool definitions

**Key Functions**:

- `behaviour_db_tool()`: Returns behaviour database tool function
- `create_behaviour_db_function_tool()`: Creates FunctionDeclaration for Gemini models
- `get_behaviour_db_tool()`: Returns ADK FunctionTool wrapper

**Purpose**: Centralizes behaviour database tool definitions to prevent duplication and circular imports. Used by both coach orchestrator and ADK agent for consistent tool integration.

### Behaviour Engine (behaviour_engine.py)

**Responsibility**: Behavior pattern detection and intervention mapping

**Key Functions**:

- `analyse_behaviour()`: Primary analysis function (tries LLM, falls back to keywords)
- `_analyse_behaviour_keyword()`: Keyword-based principle detection
- `_apply_adaptive_weighting()`: Adjusts confidence based on historical effectiveness
- `explain_principle()`: Generates behavioral explanations
- `get_interventions()`: Retrieves intervention suggestions
- `load_behaviour_db()`: Loads behavior knowledge base

**Detection Flow**:

1. Try LLM-based analysis (if available)
2. Fall back to keyword matching
3. Apply adaptive weighting based on user history
4. Return structured AnalysisResult

### LLM Client (llm_client.py)

**Responsibility**: LLM integration for nuanced behavior analysis

**Key Functions**:

- `analyse_behaviour_with_llm()`: Main LLM analysis entry point
- `_build_llm_prompt()`: Constructs context-aware prompts
- `_parse_llm_response()`: Extracts structured data from LLM
- `_validate_principle()`: Ensures detected principles exist in DB
- `_build_memory_context()`: Formats user context for LLM

**LLM Configuration**:

- Model: Gemini 2.0 Flash (configurable)
- Temperature: 0.3 (for consistent analysis)
- Tool: behaviour_analysis function declaration

### Memory Manager (memory.py)

**Responsibility**: User state persistence and retrieval

**Key Capabilities**:

- Goal tracking
- Streak management
- Struggle recording
- Conversation history
- Intervention feedback
- User profile personalization

**Serialization**:

- JSON file-based persistence
- ADK session state integration
- Type-safe serialization/deserialization

### Memory Service (memory_service.py)

**Responsibility**: Business logic for memory operations

**Static Methods**:

- `record_interaction()`: Records streak updates, struggles, interventions
- `record_feedback()`: Tracks intervention effectiveness
- `calculate_principle_effectiveness()`: Computes success rates
- `get_recent_struggles()`: Retrieves latest struggles
- `get_active_streaks()`: Filters active habits
- `get_broken_streaks()`: Identifies rebuilding opportunities
- `get_principle_usage_count()`: Counts principle applications

## Data Flow

### Interaction Flow

1. **Input Reception**
   - User provides message through CLI or notebook
   - Message includes context (goals, current state)

2. **Context Loading**
   - Coach loads UserMemory from file/session
   - Memory includes goals, streaks, conversation history

3. **Behavior Analysis**
   - Behaviour Engine receives input + memory context
   - LLM Client attempts intelligent analysis
   - Falls back to keyword matching if needed
   - Returns AnalysisResult with principle and interventions

4. **Response Generation**
   - Low confidence → Ask clarifying questions
   - High confidence → Try ADK agent (optional)
   - Fallback → Template-based response
   - Always includes principle explanation

5. **State Update**
   - Record conversation turn
   - Update streaks/struggles as needed
   - Track intervention effectiveness
   - Save updated memory

6. **Response Delivery**
   - Return formatted coaching response
   - Include behavioral explanation
   - Provide actionable interventions

### Memory Update Flow

```mermaid
flowchart LR
    A[Interaction Outcome] --> B{Type?}
    
    B -->|Streak Update| C[Update StreakData]
    B -->|Struggle| D[Add/Update Struggle]
    B -->|Intervention| E[Record Intervention]
    
    C --> F[Calculate new current/best]
    D --> G[Increment count or add new]
    E --> H[Log principle usage]
    
    F --> I[Update timestamp]
    G --> I
    H --> I
    
    I --> J[Save to file/session]
```

## Type System

HabitLedger uses a strongly-typed domain model with dataclasses for type safety and validation.

### Core Types

**Enums**:

- `ConversationRole`: USER, ASSISTANT, SYSTEM
- `BehaviourPrincipleEnum`: LOSS_AVERSION, HABIT_LOOPS, etc.

**Data Models**:

- `Goal`: Financial goals with targets and completion status
- `StreakData`: Habit streak tracking with current/best counts
- `Struggle`: User challenges with frequency tracking
- `Intervention`: Recorded coaching actions
- `ConversationTurn`: Chat history with metadata
- `InterventionFeedback`: Effectiveness tracking per principle
- `BehaviouralPrinciple`: Knowledge base entries
- `BehaviourDatabase`: Principle collection with lookup
- `AnalysisResult`: Structured analysis output

### Type Safety Benefits

1. **Compile-time validation**: Type checkers catch errors early
2. **IDE support**: Autocomplete and inline documentation
3. **Runtime safety**: Dataclass validation prevents invalid data
4. **Serialization**: Consistent to_dict/from_dict patterns
5. **Testability**: Easy to create test fixtures

## Testing Strategy

### Test Coverage

- `test_models.py`: Dataclass validation and serialization
- `test_memory_service.py`: Business logic and state updates
- `test_behaviour_engine.py`: Principle detection and matching
- `test_coach.py`: Response generation and orchestration
- `test_utils.py`: Helper functions

### Test Fixtures

- `conftest.py` provides reusable fixtures:
  - `sample_behaviour_db`: Test behaviour database
  - `empty_memory`: Clean UserMemory instance
  - `populated_memory`: UserMemory with sample data
  - `sample_user_input`: Test scenarios

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py -v
```

## Deployment Considerations

### Environment Configuration

```bash
# Required
GOOGLE_API_KEY=your_api_key

# Optional
GOOGLE_ADK_MODEL=gemini-2.0-flash-exp
LOG_LEVEL=INFO
```

### Scalability

Current design is single-user focused. For multi-user:

1. Replace file-based persistence with database
2. Implement user authentication/sessions
3. Add rate limiting for LLM calls
4. Cache behaviour database in memory
5. Implement async processing for long operations

### Observability

See [OBSERVABILITY.md](OBSERVABILITY.md) for:

- Structured logging patterns
- Performance metrics
- Decision tracing
- Error handling
