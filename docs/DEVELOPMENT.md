# HabitLedger Development Guide

This guide covers setup, development workflows, testing, and migration guidelines for HabitLedger contributors and users upgrading from older versions.

## Table of Contents

- [Development Setup](#development-setup)
  - [Prerequisites](#prerequisites)
  - [Quick Setup](#quick-setup)
  - [Full Setup Instructions](#full-setup-instructions)
  - [Why These Requirements Matter](#why-these-requirements-matter)
  - [Configuration Files Overview](#configuration-files-overview)
  - [Enforcement Mechanisms](#enforcement-mechanisms)
  - [Troubleshooting Setup](#troubleshooting-setup)
- [Quick Reference](#quick-reference)
  - [Daily Workflow](#daily-workflow)
  - [Common Commands](#common-commands)
  - [Git Commit Message Format](#git-commit-message-format)
  - [One-Command Setup](#one-command-setup)
  - [Health Check Before PR](#health-check-before-pr)
- [Development Workflow](#development-workflow)
  - [Code Organization Principles](#code-organization-principles)
  - [Adding a New Feature](#adding-a-new-feature)
  - [Code Style](#code-style)
- [Project Structure](#project-structure)
- [Testing](#testing)
  - [Running Tests](#running-tests)
  - [Test Coverage Goals](#test-coverage-goals)
  - [Writing Tests](#writing-tests)
  - [Test Categories](#test-categories)
- [Contributing](#contributing)
  - [Contribution Workflow](#contribution-workflow)
  - [Pull Request Guidelines](#pull-request-guidelines)
  - [Code Review Checklist](#code-review-checklist)
  - [Getting Help](#getting-help)
- [Development Tips](#development-tips)
  - [Debugging](#debugging)
  - [Performance Profiling](#performance-profiling)
  - [IDE Setup](#ide-setup)
  - [Useful Commands](#useful-commands)
- [Emergency Recovery](#emergency-recovery)
  - [Reset Everything](#reset-everything)
  - [Rollback to Previous Version](#rollback-to-previous-version)

## Development Setup

### Prerequisites

- **Python 3.13.2** (exact version required)
- **Git** (for version control)
- **Virtual environment** support

### Quick Setup

Run the automated setup verification:

```bash
./verify_setup.sh
```

This script checks if you have the correct Python version, virtual environment, and tools installed.

### Full Setup Instructions

1. Install Python 3.13.2

    **Using pyenv (recommended):**

    ```bash
    # Install pyenv if not already installed
    curl https://pyenv.run | bash

    # Install Python 3.13.2
    pyenv install 3.13.2

    # Set as local version for this project
    pyenv local 3.13.2

    # Verify
    python --version  # Should output: Python 3.13.2
    ```

    **Alternative methods:**

    - **Ubuntu/Debian:** `sudo apt install python3.13`
    - **macOS (Homebrew):** `brew install python@3.13`
    - **Windows:** Download from [python.org](https://www.python.org/downloads/release/python-3132/)

2. Clone Repository

    ```bash
    git clone https://github.com/sonalip9/habitledger-agent.git
    cd habitledger-agent
    ```

3. Create Virtual Environment

    ```bash
    # Create .venv
    python -m venv .venv
    # Activate it
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate     # Windows

    # Verify Python version in venv
    python --version  # Should still be 3.13.2
    ```

4. Install Dependencies

    ```bash
    # Upgrade pip
    pip install --upgrade pip
    # Install project dependencies
    pip install -r requirements.txt
    ```

5. Setup nbstripout

    nbstripout automatically strips output and metadata from Jupyter notebooks before committing to git.

    ```bash
    # Install nbstripout (should already be in requirements.txt)
    pip install nbstripout

    # Configure for this repository
    nbstripout --install

    # Verify installation
    nbstripout --status
    ```

6. (Optional) Setup Pre-commit Hooks

    Pre-commit hooks automatically format code and strip notebooks on every commit:

    ```bash
    # Install pre-commit
    pip install pre-commit

    # Install the hooks
    pre-commit install

    # Test the hooks (optional)
    pre-commit run --all-files
    ```

7. Configure Environment Variables

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

8. Verify Installation

    ```bash
    # Run setup verification
    ./verify_setup.sh

    # Run tests
    pytest tests/

    # Try the CLI
    python -m src.coach
    ```

### Why These Requirements Matter

**Python 3.13.2 (Exact Version):**

- Ensures consistent behavior across all development environments
- Prevents "works on my machine" issues
- Matches production deployment requirements
- Easier debugging with consistent Python version

**Virtual Environment (.venv):**

- Isolates project dependencies from system packages
- Prevents conflicts between different projects
- Makes dependency management reproducible
- Easier to reset if something breaks

**nbstripout (Notebook Hygiene):**

- Keeps git history clean (no large output diffs)
- Reduces repository size significantly
- Prevents merge conflicts from notebook metadata
- Protects against accidental credential leaks in outputs
- Improves code review quality (focus on code, not outputs)

### Configuration Files Overview

The project includes several configuration files that enforce these standards:

| File | Purpose | Enforces |
|------|---------|----------|
| `.python-version` | Specifies Python 3.13.2 for pyenv | Python version |
| `pyproject.toml` | Tool configurations and version constraints | Python ≥3.13.2 |
| `.pre-commit-config.yaml` | Git hooks (nbstripout, black, ruff) | Code quality |
| `.vscode/settings.json` | VS Code workspace settings | .venv, formatters |
| `.github/copilot-instructions.md` | AI assistant guidelines | All standards |

### Enforcement Mechanisms

The project uses **layered enforcement** to ensure standards are followed:

1. **pyenv + `.python-version`** → Auto-selects Python 3.13.2 when you `cd` into the project
2. **`pyproject.toml`** → pip rejects installation with older Python versions
3. **VS Code settings** → Automatically uses .venv and correct Python
4. **Pre-commit hooks** → Blocks commits that don't meet quality standards
5. **Git filters** → nbstripout strips notebooks automatically on `git add`
6. **Documentation** → Clear guidelines in README and Copilot instructions
7. **Verification script** → `./verify_setup.sh` validates everything

### Troubleshooting Setup

**Wrong Python Version:**

```bash
# Check current version
python --version

# If wrong, install 3.13.2
pyenv install 3.13.2
pyenv local 3.13.2

# Recreate venv
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
```

**Virtual Environment Not Activating:**

```bash
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# If VS Code isn't using the right Python:
# Press Ctrl+Shift+P → "Python: Select Interpreter" → choose .venv
```

**nbstripout Not Working:**

```bash
# Reinstall and reconfigure
pip install --force-reinstall nbstripout
nbstripout --install --attributes .gitattributes

# Verify
nbstripout --status
```

**Pre-commit Hooks Failing:**

```bash
# Update hooks to latest versions
pre-commit autoupdate

# Run manually to see errors
pre-commit run --all-files

# Fix issues, then commit again
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

## Quick Reference

### Daily Workflow

```bash
# Start working
cd habitledger-agent
source .venv/bin/activate  # Auto-activates in VS Code

# Before committing
./verify_setup.sh  # Optional: check everything is OK

# Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat(memory): add user preference tracking"
```

### Common Commands

| Task | Command |
|------|---------|
| Activate venv | `source .venv/bin/activate` |
| Check Python version | `python --version` |
| Install new package | `pip install <package> && pip freeze > requirements.txt` |
| Run tests | `pytest tests/` |
| Run tests with coverage | `pytest tests/ --cov=src --cov-report=html` |
| Format code | `black src/ tests/` |
| Lint code | `ruff check src/ tests/` |
| Type check | `mypy src/` |
| Strip notebook | `nbstripout notebooks/demo.ipynb` |
| Check setup | `./verify_setup.sh` |
| Run pre-commit | `pre-commit run --all-files` |

### Git Commit Message Format

Follow **Conventional Commits** pattern:

```text
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `docs`: Documentation
- `test`: Tests
- `chore`: Maintenance
- `style`: Formatting
- `perf`: Performance
- `ci`: CI/CD
- `build`: Build system

**Examples:**

```bash
feat(engine): add adaptive weighting based on intervention history
fix(memory): handle missing last_updated field in streak data
refactor(coach): decompose run_once into smaller helper functions
docs(architecture): add component interaction flowchart
test(models): add serialization tests for all dataclasses
chore(deps): upgrade google-adk to 0.1.5
```

### One-Command Setup

For fresh setup on a new machine:

```bash
python3.13 -m venv .venv && \
source .venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt && \
nbstripout --install && \
pre-commit install && \
./verify_setup.sh
```

### Health Check Before PR

Run before creating a pull request:

```bash
# 1. Verify setup
./verify_setup.sh

# 2. Run tests with coverage
pytest tests/ --cov=src

# 3. Check code quality
black --check src/ tests/
ruff check src/ tests/

# 4. Check notebooks
nbstripout --check notebooks/*.ipynb

# All should pass ✅
```

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

## Emergency Recovery

### Reset Everything

If your environment is broken:

```bash
# Nuclear option (destroys local changes)
git clean -fdx  # Remove all untracked files
rm -rf .venv    # Remove virtual environment

# Then re-setup:
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
nbstripout --install
pre-commit install
./verify_setup.sh
```

### Rollback to Previous Version

If you encounter breaking changes:

```bash
# Backup your data
cp data/user_memory.json data/user_memory.json.backup

# Check out previous version
git checkout v1.0.0  # Replace with your previous version

# Restore dependencies
pip install -r requirements.txt
```
