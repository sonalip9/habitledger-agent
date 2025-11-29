# HabitLedger Development Guide

This guide covers setup, development workflows, testing, and migration guidelines for HabitLedger contributors and users upgrading from older versions.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, conda, or similar)
- Google API key for Gemini (optional but recommended)

### Initial Setup

1. **Clone the repository**

    ```bash
    git clone https://github.com/sonalip9/habitledger-agent.git
    cd habitledger-agent
    ```

2. **Create virtual environment**

    ```bash
    python -m venv .venv

    # Activate on macOS/Linux
    source .venv/bin/activate

    # Activate on Windows
    .venv\Scripts\activate
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment**

    Create `.env` file:

    ```bash
    # Required for LLM-based analysis
    GOOGLE_API_KEY=your_api_key_here

    # Optional configuration (defaults shown)
    GOOGLE_ADK_MODEL=gemini-1.5-flash
    LLM_MIN_CALL_INTERVAL=1.0
    LOG_LEVEL=INFO
    STRUCTURED_LOGGING=false
    ```

5. **Verify installation**

    ```bash
    # Run tests
    pytest tests/

    # Try the CLI
    python -m src.coach
    ```

## Project Structure

```markdown
habitledger-agent/
├── src/                        # Source code
│   ├── models.py              # Typed domain models
│   ├── memory.py              # Memory and persistence
│   ├── memory_service.py      # Business logic for memory
│   ├── behaviour_engine.py    # Principle detection
│   ├── llm_client.py          # LLM integration
│   ├── coach.py               # Main orchestrator
│   ├── config.py              # Configuration
│   ├── adk_config.py          # Shared ADK configuration
│   ├── adk_tools.py           # Shared ADK tool definitions
│   ├── utils.py               # Utilities
│   ├── session_db.py          # Session management
│   ├── templates.py           # Response templates
│   └── habitledger_adk/       # ADK integration
│       ├── agent.py           # ADK agent
│       └── runner.py          # ADK CLI runner
│
├── data/
│   └── behaviour_principles.json  # Knowledge base
│
├── tests/                     # Test suite
│   ├── conftest.py           # Pytest fixtures
│   ├── test_models.py        # Model tests
│   ├── test_memory_service.py  # Service tests
│   ├── test_behaviour_engine.py  # Engine tests
│   ├── test_coach.py         # Coach tests
│   ├── test_utils.py         # Utility tests
│   ├── test_evaluation.py   # Evaluation tests
│   └── test_llm_integration.py  # LLM tests
│
├── notebooks/
│   └── demo.ipynb            # Interactive demo
│
├── examples/
│   └── observability_demo.py  # Logging examples
│
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md       # Architecture guide
│   ├── DEVELOPMENT.md        # This file
│   ├── OBSERVABILITY.md      # Logging guide
│   └── EVALUATION_RESULTS.md  # Test results
│
├── requirements.txt          # Dependencies
├── README.md                 # Main documentation
└── .env                      # Environment config (not committed)
```

### Key Directories

- **src/**: All application code with clear module boundaries
- **tests/**: Comprehensive test suite with >80% coverage goal
- **data/**: Static data files (behaviour principles knowledge base)
- **docs/**: Architecture, development, and usage documentation
- **notebooks/**: Interactive demos and examples
- **examples/**: Standalone example scripts

## Development Workflow

### Code Organization Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Type Safety**: Use typed models (dataclasses) throughout
3. **Dependency Injection**: Avoid global state, pass dependencies explicitly
4. **Testability**: Write testable code with clear interfaces
5. **Documentation**: Docstrings for all public functions and classes

### Adding a New Feature

1. **Create branch**

    ```bash
    git checkout -b feature/your-feature-name
    ```

2. **Define types** (if needed)

    Add new dataclasses to `src/models.py`:

    ```python
    @dataclass
    class NewFeature:
        """Description of the new feature."""
        field1: str
        field2: int
        
        def to_dict(self) -> dict[str, Any]:
            return {"field1": self.field1, "field2": self.field2}
        
        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> "NewFeature":
            return cls(field1=data["field1"], field2=data["field2"])
    ```

3. **Implement feature**

    Follow module boundaries:

    - Data models → `models.py`
    - Memory operations → `memory.py` or `memory_service.py`
    - Analysis logic → `behaviour_engine.py`
    - LLM integration → `llm_client.py`
    - Orchestration → `coach.py`

4. **Write tests**

    Create test file in `tests/`:

    ```python
    import pytest
    from src.your_module import your_function

    class TestYourFeature:
        def test_basic_functionality(self):
            result = your_function(...)
            assert result == expected
    ```

5. **Run tests**

    ```bash
    pytest tests/ --cov=src
    ```

6. **Update documentation**

    Add to relevant docs:

    - Architecture diagrams (`docs/ARCHITECTURE.md`)
    - Usage examples (`README.md`)
    - API documentation (docstrings)

7. **Commit and push**

    ```bash
    git add .
    git commit -m "feat: add your feature description"
    git push origin feature/your-feature-name
    ```

### Code Style

- Follow PEP 8
- Use type hints
- Keep functions focused and small (<50 lines)
- Write descriptive variable names
- Add docstrings to public functions
- Use f-strings for formatting
- Prefer dataclasses over dicts for structured data

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_models.py -v

# Run specific test
pytest tests/test_models.py::TestGoal::test_goal_creation -v
```

### Test Coverage Goals

Target coverage by module:

- `models.py`: 100% (dataclasses and serialization)
- `memory_service.py`: >90% (business logic)
- `behaviour_engine.py`: >85% (core detection logic)
- `coach.py`: >80% (orchestration with mocked dependencies)
- `llm_client.py`: >70% (requires API mocking)

### Writing Tests

Use fixtures from `conftest.py`:

```python
def test_example(empty_memory, sample_behaviour_db):
    # Test with clean state
    result = some_function(empty_memory, sample_behaviour_db)
    assert result is not None
```

Create new fixtures as needed:

```python
@pytest.fixture
def custom_fixture():
    """Description of fixture."""
    # Setup
    data = create_test_data()
    yield data
    # Teardown (if needed)
```

### Test Categories

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test component interactions
3. **End-to-End Tests**: Test complete user flows
4. **Regression Tests**: Prevent known bugs from reappearing

## Contributing

### Contribution Workflow

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Run full test suite
5. Update documentation
6. Submit pull request

### Pull Request Guidelines

- **Title**: Clear, descriptive (e.g., "feat: add streak visualization")
- **Description**: Explain what and why
- **Tests**: Include tests for new features
- **Documentation**: Update relevant docs
- **Coverage**: Maintain or improve coverage

### Code Review Checklist

- [ ] Tests pass locally
- [ ] Coverage maintained/improved
- [ ] Documentation updated
- [ ] Type hints added
- [ ] Docstrings written
- [ ] No breaking changes (or documented)
- [ ] Follows code style guidelines

### Getting Help

- **Documentation**: Check `docs/` directory
- **Issues**: Search existing GitHub issues
- **Questions**: Open discussion on GitHub
- **Bugs**: Open issue with reproduction steps

## Development Tips

### Debugging

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m src.coach
```

### Performance Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### IDE Setup

**VS Code**:

- Install Python extension
- Enable type checking (Pylance)
- Configure pytest for test discovery

**PyCharm**:

- Mark `src/` as sources root
- Configure pytest as default test runner
- Enable type checking

### Useful Commands

```bash
# Format code
black src/ tests/

# Type checking
mypy src/

# Lint
ruff check src/ tests/

# Run specific test category
pytest tests/ -m unit

# Generate coverage HTML report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```
