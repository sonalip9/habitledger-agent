# GitHub Copilot Instructions for HabitLedger Agent

## Project Overview

HabitLedger is an AI-powered behavioural money coach built using Google's Agent Development Kit (ADK). This project follows clean architecture principles with strongly-typed domain models, comprehensive testing, and detailed observability.

**Project Type:** AI Agent (Concierge Track - Kaggle Competition)  
**Primary Language:** Python 3.10+  
**Framework:** Google ADK, Gemini 2.0 Flash  
**Architecture:** Modular, event-driven, stateful agent system

## Core Principles

### 1. Code Organization

- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Type Safety**: Use typed models (dataclasses) throughout the codebase
- **Dependency Injection**: Avoid global state, pass dependencies explicitly
- **No Circular Dependencies**: Use shared configuration/tool modules to break cycles
- **Testability**: Write testable code with clear interfaces

### 2. Architecture Patterns

**Module Structure:**
- `src/models.py` - Typed domain models (dataclasses with serialization)
- `src/memory.py` - State persistence and retrieval
- `src/memory_service.py` - Business logic for memory operations
- `src/behaviour_engine.py` - Principle detection and intervention mapping
- `src/llm_client.py` - LLM integration with fallback mechanisms
- `src/coach.py` - Main orchestrator for agent interactions
- `src/adk_config.py` - Shared ADK configuration (prevents circular imports)
- `src/adk_tools.py` - Shared ADK tool definitions (prevents circular imports)
- `src/habitledger_adk/agent.py` - ADK agent implementation
- `src/habitledger_adk/runner.py` - ADK CLI runner

**Key Design Patterns:**
- **Orchestrator Pattern**: `coach.py` coordinates all components
- **Service Layer**: `memory_service.py` contains business logic
- **Strategy Pattern**: LLM-based analysis with keyword-based fallback
- **Repository Pattern**: `memory.py` handles data persistence
- **Tool Pattern**: `behaviour_principles.json` acts as external knowledge base

### 3. Dependency Flow

```
adk_config.py (no dependencies)
     ↑
     |
coach.py ← memory.py ← memory_service.py
     ↑
     |
adk_tools.py ← behaviour_engine.py ← llm_client.py
     ↑
     |
habitledger_adk/agent.py
```

**NEVER create circular imports.** If you need shared code between `coach.py` and `habitledger_adk/agent.py`, extract it to `adk_config.py` or `adk_tools.py`.

## Coding Standards

### 1. Type Hints

Always use type hints for function parameters and return values:

```python
def analyse_behaviour(
    user_input: str,
    memory: UserMemory,
    behaviour_db: BehaviourDatabase
) -> AnalysisResult:
    """Analyze user behaviour and return structured result."""
    pass
```

### 2. Dataclass Models

Use dataclasses for all domain models with serialization methods:

```python
@dataclass
class Goal:
    """User financial goal with target and completion status."""
    description: str
    target: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed: bool = False
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "target": self.target,
            "created_at": self.created_at,
            "completed": self.completed
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Goal":
        return cls(
            description=data["description"],
            target=data["target"],
            created_at=data.get("created_at", datetime.now().isoformat()),
            completed=data.get("completed", False)
        )
```

### 3. Function Size and Complexity

- Keep functions focused and small (<50 lines)
- Extract helper functions for complex logic
- Use descriptive variable names
- Add docstrings to all public functions

**Example of proper decomposition:**

```python
# BAD: Large monolithic function
def process_request(user_input, memory, db):
    # 100+ lines of mixed logic
    pass

# GOOD: Decomposed into smaller functions
def process_request(user_input: str, memory: UserMemory, db: BehaviourDatabase) -> str:
    """Process user request and return coaching response."""
    analysis = _analyze_input(user_input, memory, db)
    response = _build_response(analysis, memory)
    _update_state(memory, analysis)
    return response

def _analyze_input(user_input: str, memory: UserMemory, db: BehaviourDatabase) -> AnalysisResult:
    """Analyze user input and detect behavioural patterns."""
    # Focused analysis logic
    pass

def _build_response(analysis: AnalysisResult, memory: UserMemory) -> str:
    """Build coaching response from analysis."""
    # Focused response building
    pass

def _update_state(memory: UserMemory, analysis: AnalysisResult) -> None:
    """Update memory with interaction results."""
    # Focused state update
    pass
```

### 4. Error Handling

Use specific exceptions and provide context:

```python
try:
    result = llm_client.analyse_behaviour(input, memory, db)
except Exception as e:
    logger.error(f"LLM analysis failed: {e}", exc_info=True)
    # Fall back to keyword-based analysis
    result = _analyse_behaviour_keyword(input, db)
```

### 5. Logging

Use structured logging with event types:

```python
from src.utils import log_event

# Log decisions and reasoning
log_event(
    "principle_detected",
    {
        "principle_id": principle.id,
        "confidence": 0.85,
        "method": "llm",
        "reasoning": "User mentioned impulse spending on food delivery"
    }
)

# Log performance metrics
log_event(
    "llm_latency",
    {"duration_ms": elapsed_ms, "model": model_name}
)

# Log errors with context
log_event(
    "analysis_error",
    {"error": str(e), "fallback": "keyword_matching"},
    level="ERROR"
)
```

## Commit Message Guidelines

Follow the **Conventional Commits** pattern:

### Format

```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature or enhancement
- `fix`: Bug fix
- `refactor`: Code restructuring without changing functionality
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (dependencies, config)
- `style`: Code style changes (formatting, whitespace)
- `perf`: Performance improvements
- `ci`: CI/CD changes
- `build`: Build system changes

### Scopes (optional but recommended)

- `models`: Domain model changes
- `memory`: Memory/persistence changes
- `coach`: Coach orchestrator changes
- `engine`: Behaviour engine changes
- `llm`: LLM client changes
- `adk`: ADK integration changes
- `tests`: Test suite changes
- `docs`: Documentation changes
- `config`: Configuration changes

### Examples

```bash
# Good commit messages
feat(engine): add adaptive weighting based on intervention history
fix(memory): handle missing last_updated field in streak data
refactor(coach): decompose run_once into smaller helper functions
docs(architecture): add component interaction flowchart
test(models): add serialization tests for all dataclasses
chore(deps): upgrade google-adk to 0.1.5

# Bad commit messages (avoid these)
update code
fix bug
changes
wip
test
```

### Multi-line Commits

For complex changes, use the body to explain:

```bash
feat(llm): add context-aware prompt building

- Include user goals and recent struggles in prompts
- Add memory context formatter
- Improve principle validation with fallback logic

This change improves LLM analysis accuracy by providing
richer context about the user's financial behaviour patterns.
```

## Testing Requirements

### 1. Test Coverage Goals

- **models.py**: 100% (dataclasses and serialization)
- **memory_service.py**: >90% (business logic)
- **behaviour_engine.py**: >85% (core detection logic)
- **coach.py**: >80% (orchestration)
- **llm_client.py**: >70% (requires mocking)

### 2. Writing Tests

Use fixtures from `conftest.py`:

```python
def test_record_interaction(empty_memory, sample_behaviour_db):
    """Test recording user interaction updates memory correctly."""
    principle = sample_behaviour_db.principles[0]
    
    MemoryService.record_interaction(
        memory=empty_memory,
        principle_id=principle.id,
        success=True,
        context="User completed savings goal"
    )
    
    assert empty_memory.intervention_feedback[principle.id].successes == 1
    assert empty_memory.intervention_feedback[principle.id].success_rate == 1.0
```

### 3. Test Categories

Mark tests with appropriate categories:

```python
@pytest.mark.unit
def test_goal_creation():
    """Test Goal dataclass creation."""
    pass

@pytest.mark.integration
def test_coach_with_llm():
    """Test coach orchestration with LLM integration."""
    pass

@pytest.mark.slow
def test_large_dataset_processing():
    """Test processing large conversation history."""
    pass
```

### 4. Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific category
pytest tests/ -m unit

# Run specific file
pytest tests/test_models.py -v
```

## Common Development Tasks

### Adding a New Dataclass

1. Add to `src/models.py`:
```python
@dataclass
class NewFeature:
    """Description of the feature."""
    field1: str
    field2: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict[str, Any]:
        return {"field1": self.field1, "field2": self.field2}
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NewFeature":
        return cls(field1=data["field1"], field2=data["field2"])
```

2. Update `UserMemory` if needed:
```python
@dataclass
class UserMemory:
    # ... existing fields ...
    new_features: list[NewFeature] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        data = {
            # ... existing serialization ...
            "new_features": [f.to_dict() for f in self.new_features]
        }
        return data
```

3. Add tests in `tests/test_models.py`:
```python
class TestNewFeature:
    def test_creation(self):
        feature = NewFeature(field1="value", field2=42)
        assert feature.field1 == "value"
    
    def test_serialization(self):
        feature = NewFeature(field1="value", field2=42)
        data = feature.to_dict()
        restored = NewFeature.from_dict(data)
        assert restored.field1 == feature.field1
```

### Adding Business Logic

Add methods to `MemoryService` (not directly to `UserMemory`):

```python
class MemoryService:
    @staticmethod
    def new_operation(memory: UserMemory, param: str) -> ResultType:
        """Description of what this operation does.
        
        Args:
            memory: User memory to operate on
            param: Description of parameter
            
        Returns:
            Description of return value
        """
        # Business logic here
        pass
```

### Adding a New Behaviour Principle

1. Add to `data/behaviour_principles.json`:
```json
{
  "id": "new_principle",
  "name": "New Principle Name",
  "description": "Clear description of the principle",
  "typical_triggers": ["trigger1", "trigger2"],
  "interventions": [
    "Specific action 1",
    "Specific action 2"
  ]
}
```

2. Add enum value to `models.py`:
```python
class BehaviourPrincipleEnum(str, Enum):
    # ... existing values ...
    NEW_PRINCIPLE = "new_principle"
```

3. Update tests:
```python
def test_new_principle_detection(sample_behaviour_db):
    """Test detection of new principle."""
    user_input = "I always do X when Y happens"
    result = analyse_behaviour(user_input, empty_memory, sample_behaviour_db)
    assert result.principle.id == "new_principle"
```

### Fixing Circular Import Issues

If you encounter circular imports:

1. **Extract shared configuration** to `adk_config.py`:
```python
# adk_config.py
SHARED_CONSTANT = "value"
```

2. **Extract shared tools** to `adk_tools.py`:
```python
# adk_tools.py
def shared_tool_function():
    """Shared tool implementation."""
    pass
```

3. **Update imports** in affected modules:
```python
# coach.py
from src.adk_config import SHARED_CONSTANT
from src.adk_tools import shared_tool_function

# habitledger_adk/agent.py  
from src.adk_config import SHARED_CONSTANT
from src.adk_tools import shared_tool_function
```

**NEVER use local imports inside functions** as a workaround. Always extract shared code.

## Documentation Requirements

### 1. Docstrings

All public functions and classes must have docstrings:

```python
def analyse_behaviour(
    user_input: str,
    memory: UserMemory,
    behaviour_db: BehaviourDatabase
) -> AnalysisResult:
    """Analyze user behaviour and detect relevant principles.
    
    Attempts LLM-based analysis first, falls back to keyword matching
    if LLM is unavailable or returns invalid results.
    
    Args:
        user_input: User message describing their financial situation
        memory: User memory with goals, streaks, and history
        behaviour_db: Behaviour principles knowledge base
        
    Returns:
        AnalysisResult containing detected principle, interventions,
        confidence score, and reasoning
        
    Raises:
        ValueError: If behaviour_db is empty or invalid
    """
    pass
```

### 2. Updating Documentation

When making significant changes, update relevant docs:

- **Architecture changes**: Update `docs/ARCHITECTURE.md` with diagrams
- **New features**: Update `README.md` with usage examples
- **Breaking changes**: Update `docs/DEVELOPMENT.md` migration guide
- **API changes**: Update inline docstrings

### 3. Code Comments

Add comments for complex logic:

```python
# Apply adaptive weighting based on historical effectiveness
# This boosts confidence for principles that have worked well for this user
if principle.id in memory.intervention_feedback:
    feedback = memory.intervention_feedback[principle.id]
    effectiveness = feedback.success_rate
    adjusted_confidence = base_confidence * (0.5 + 0.5 * effectiveness)
```

## Environment and Configuration

### Required Environment Variables

```bash
# Required for LLM-based analysis
GOOGLE_API_KEY=your_api_key_here

# Optional configuration
GOOGLE_ADK_MODEL=gemini-2.0-flash-exp  # Default model
LOG_LEVEL=INFO                         # Logging level (DEBUG, INFO, WARNING, ERROR)
```

### Configuration Loading

Always use the config module:

```python
from src.config import get_api_key, get_model_name

api_key = get_api_key()  # Handles missing keys gracefully
model = get_model_name()  # Returns default if not set
```

## LLM Integration Guidelines

### 1. Always Provide Fallback

Never rely solely on LLM calls:

```python
def analyse_behaviour(user_input: str, memory: UserMemory, db: BehaviourDatabase) -> AnalysisResult:
    """Analyze behaviour with LLM, fall back to keywords."""
    try:
        # Try LLM-based analysis first
        result = llm_client.analyse_behaviour_with_llm(user_input, memory, db)
        if result.principle:
            return result
    except Exception as e:
        logger.warning(f"LLM analysis failed: {e}, falling back to keywords")
    
    # Fall back to keyword-based analysis
    return _analyse_behaviour_keyword(user_input, db)
```

### 2. Log LLM Decisions

Always log what the LLM decided and why:

```python
log_event(
    "llm_analysis_complete",
    {
        "principle_detected": result.principle.id,
        "confidence": result.confidence,
        "reasoning": result.reasoning,
        "model": model_name,
        "duration_ms": elapsed_ms
    }
)
```

### 3. Validate LLM Outputs

Never trust LLM outputs blindly:

```python
# Validate that detected principle exists in knowledge base
if principle_id not in behaviour_db.get_all_principle_ids():
    logger.warning(f"LLM returned invalid principle: {principle_id}")
    return None  # Fall back to keyword matching
```

## Memory and State Management

### 1. Use MemoryService for Business Logic

Don't manipulate memory directly in orchestrator code:

```python
# BAD: Direct manipulation in coach.py
memory.streaks["no_delivery"].current += 1
memory.streaks["no_delivery"].last_updated = datetime.now().isoformat()

# GOOD: Use MemoryService
MemoryService.record_interaction(
    memory=memory,
    principle_id=principle.id,
    success=True,
    context="User maintained streak"
)
```

### 2. Always Save After Updates

```python
def run_once(user_input: str, memory: UserMemory, db: BehaviourDatabase) -> str:
    """Process user input and return response."""
    # ... process input ...
    
    # Update memory
    memory.add_conversation_turn("user", user_input)
    memory.add_conversation_turn("assistant", response)
    
    # Save to disk
    memory.save_to_file()
    
    return response
```

### 3. Serialize Complex Objects

Always implement `to_dict()` and `from_dict()` for all domain models:

```python
@dataclass
class ComplexModel:
    nested_objects: list[OtherModel]
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "nested_objects": [obj.to_dict() for obj in self.nested_objects]
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ComplexModel":
        return cls(
            nested_objects=[OtherModel.from_dict(d) for d in data["nested_objects"]]
        )
```

## Observability Best Practices

### 1. Event Types

Use consistent event types across the codebase:

- `principle_detected` - Behaviour principle identified
- `intervention_suggested` - Intervention recommended
- `llm_analysis_complete` - LLM analysis finished
- `memory_updated` - User state changed
- `streak_updated` - Habit streak changed
- `confidence_low` - Low confidence detection
- `analysis_error` - Analysis failed

### 2. Performance Metrics

Log performance-critical operations:

```python
import time

start_time = time.time()
result = expensive_operation()
elapsed_ms = (time.time() - start_time) * 1000

log_event(
    "operation_completed",
    {
        "duration_ms": elapsed_ms,
        "operation": "llm_analysis",
        "success": result is not None
    }
)
```

### 3. Decision Transparency

Log all AI decisions with reasoning:

```python
log_event(
    "principle_selected",
    {
        "principle_id": principle.id,
        "principle_name": principle.name,
        "confidence": confidence_score,
        "method": "llm" if used_llm else "keyword",
        "reasoning": "User mentioned impulse spending triggers",
        "interventions_count": len(interventions)
    }
)
```

## ADK Integration Guidelines

### 1. Tool Definitions

Define tools in `adk_tools.py` for reusability:

```python
def my_tool_function(param: str) -> dict[str, Any]:
    """Tool function implementation."""
    # Tool logic here
    return {"result": "value"}

def create_my_tool() -> FunctionDeclaration:
    """Create tool declaration for Gemini."""
    return FunctionDeclaration(
        name="my_tool",
        description="Clear description for LLM",
        parameters={
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "Parameter description"}
            },
            "required": ["param"]
        }
    )
```

### 2. Agent Instructions

Store agent instructions in `adk_config.py`:

```python
INSTRUCTION_TEXT = """
You are a behavioural money coach...

[Clear, detailed instructions for the agent]
"""
```

### 3. Error Handling in ADK Agents

Always handle tool call errors gracefully:

```python
def handle_tool_call(tool_name: str, args: dict) -> str:
    """Handle tool call from ADK agent."""
    try:
        if tool_name == "my_tool":
            result = my_tool_function(**args)
            return json.dumps(result)
    except Exception as e:
        logger.error(f"Tool call failed: {e}", exc_info=True)
        return json.dumps({"error": str(e)})
```

## Common Pitfalls to Avoid

### 1. Don't Use Dicts for Structured Data

```python
# BAD: Dict-based data
goal = {"description": "Save money", "target": "₹5000"}

# GOOD: Typed model
goal = Goal(description="Save money", target="₹5000")
```

### 2. Don't Mix Business Logic with Data Access

```python
# BAD: Business logic in coach.py
memory.streaks[habit].current += 1
if memory.streaks[habit].current > memory.streaks[habit].best:
    memory.streaks[habit].best = memory.streaks[habit].current

# GOOD: Use service layer
MemoryService.update_streak(memory, habit, success=True)
```

### 3. Don't Skip Type Hints

```python
# BAD: No type hints
def process(data, config):
    return something

# GOOD: Full type hints
def process(data: dict[str, Any], config: Config) -> ProcessResult:
    return something
```

### 4. Don't Use Magic Numbers

```python
# BAD: Magic number
if confidence > 0.6:
    do_something()

# GOOD: Named constant
CONFIDENCE_THRESHOLD = 0.6
if confidence > CONFIDENCE_THRESHOLD:
    do_something()
```

### 5. Don't Silently Catch Exceptions

```python
# BAD: Silent failure
try:
    result = risky_operation()
except:
    pass

# GOOD: Log and handle
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}", exc_info=True)
    # Provide fallback or re-raise
```

## Code Review Checklist

Before committing, ensure:

- [ ] All functions have type hints
- [ ] All public functions have docstrings
- [ ] Tests added for new features
- [ ] No circular imports
- [ ] Logging added for important operations
- [ ] Error handling in place with fallbacks
- [ ] Code follows <50 lines per function guideline
- [ ] Commit message follows conventional commits format
- [ ] Documentation updated if needed
- [ ] Tests pass: `pytest tests/`
- [ ] Code formatted: `black src/ tests/`
- [ ] No linting errors: `ruff check src/ tests/`

## Getting Help

- **Architecture**: See `docs/ARCHITECTURE.md`
- **Development**: See `docs/DEVELOPMENT.md`
- **Testing**: See test examples in `tests/`
- **Observability**: See `docs/OBSERVABILITY.md`
- **API Docs**: Check inline docstrings

## Project-Specific Conventions

### File Naming

- Module files: `snake_case.py`
- Test files: `test_module_name.py`
- Config files: `lowercase.py` or `UPPERCASE.md`

### Variable Naming

- Functions/methods: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`

### Import Organization

```python
# Standard library
import json
import logging
from datetime import datetime
from typing import Any, Optional

# Third-party
from google import genai
import pytest

# Local
from src.models import Goal, UserMemory
from src.memory_service import MemoryService
from src.utils import log_event
```

---

**Remember:** This is an AI agent project focused on behavioral coaching. Every change should consider the user experience, maintain state consistency, and provide transparent, explainable behavior. Quality over speed, clarity over cleverness.
