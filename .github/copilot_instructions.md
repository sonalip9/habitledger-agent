# GitHub Copilot Agent Instructions for HabitLedger

This document describes how GitHub Copilot (and other AI coding assistants) should behave when generating code, tests, documentation, or other artifacts for the **HabitLedger** project.

The goal is to keep the codebase **clean, maintainable, well-documented, and consistent** with the project's conventions.

---

## 1. Repository Context

- Project name: **HabitLedger**
- Description: Behavioural money coach that helps users build healthier financial habits using behavioural science.
- Primary language: **Python**
- Main components:
  - `src/` – core agent logic and utilities
  - `data/` – behaviour principles and static data
  - `notebooks/` – demo and experimentation notebooks
  - `tests/` – tests for core functionality

Whenever you generate or modify code, align with the goals and structure of this project.

---

## 2. Commit Message Rules

All commit messages **must** follow the **Conventional Commits** specification:

**Format:**

```text
<type>(optional scope): <short description>
````

**Examples:**

- `feat(agent): add daily check-in flow`
- `fix(memory): correct streak persistence bug`
- `docs(readme): update project overview`
- `refactor(engine): simplify behaviour classification`
- `test(coach): add unit tests for response generation`
- `chore(deps): bump openai library version`

**Rules:**

- Use only lower case for `type` and `scope`.
- Keep the description short and action-focused.
- Avoid combining multiple unrelated changes in a single commit.

---

## 3. Commit Size and Change Granularity

Commits **must be small and focused**:

- A **single commit should represent a single logical change**.
- Do **not** mix refactors, new features, and documentation updates in one commit.
- If a change affects multiple areas (e.g., code + tests + docs), split into multiple commits when possible:

  - One commit for code
  - One commit for tests
  - One commit for documentation

Examples of good commit boundaries:

- Adding a new function or module.
- Fixing a single bug.
- Updating a specific section in the README.
- Adding tests for one function or class.

---

## 4. Code Style and Structure

### 4.1 Single-Purpose Functions

All generated code should follow **single-responsibility** principles:

- Each function should do **one thing well**.
- If a function:

  - grows too long,
  - handles multiple concerns, or
  - mixes logic (e.g., parsing + business logic + I/O),

  then split it into smaller functions.

**Examples of good function responsibilities:**

- Parsing user input.
- Selecting the behaviour principle to apply.
- Generating the coach reply.
- Saving memory/state.

### 4.2 DRY (Don’t Repeat Yourself)

- Avoid duplicating logic or code blocks.
- Extract common logic into helper functions or utility modules.
- If you see similar code appearing in multiple places, refactor it into a shared function.

### 4.3 Readability

- Use clear, descriptive names for variables, functions, and modules.
- Prefer explicitness over “clever” one-liners.
- Keep functions short and easy to scan.

---

## 5. Documentation Requirements

Every significant part of the code must be documented.

### 5.1 Docstrings

For **all public functions, classes, and modules**:

- Add a docstring that explains:

  - What it does
  - Key parameters
  - Return value
  - Any side effects, if applicable

Example (Python):

```python
def generate_habit_plan(user_state, behaviour_db):
    """
    Generate a personalised habit plan for the user.

    Args:
        user_state (dict): Current state of the user, including goals and recent behaviour.
        behaviour_db (dict): Behaviour principles and intervention strategies.

    Returns:
        dict: A structured habit plan containing actions, rationale, and suggested check-in schedule.
    """
    ...
```

### 5.2 Inline Comments

- Use inline comments **sparingly**, only when logic is non-obvious.
- Avoid repeating what the code already clearly expresses.

### 5.3 Module-Level Documentation

For new modules:

- Add a short description at the top explaining the role of the module and how it fits into the HabitLedger architecture.

---

## 6. README Maintenance

The `README.md` must be kept up to date as the project evolves.

Whenever the project behaviour, features, or usage changes, ensure:

- The **README is updated in the same work session** as the code change.
- If a new feature is added:

  - Add or update the relevant sections in the README.
- If behaviour changes:

  - Update feature descriptions or limitations.
- If the structure changes:

  - Update the project structure section.

Prefer **separate commits** for README updates when they are substantial:

- Example:

  - `feat(agent): add weekly review flow`
  - `docs(readme): document weekly review feature`

---

## 7. Tests and Reliability

- When adding new functionality that has core logic, also add or update tests in the `tests/` directory.
- Aim for small, focused tests that validate:

  - Logic in behaviour selection
  - Memory and state transitions
  - Response structure

If a bug is fixed:

- Add a test that would have caught the bug.
- Use a commit type: `fix(...)` and optionally `test(...)` for the test itself.

---

## 8. General Behaviour for Copilot (and AI Assistants)

When generating or modifying code in this repository, Copilot should:

1. **Follow the project conventions** described here.
2. **Prefer clarity over cleverness**.
3. **Suggest small, focused changes** suitable for atomic commits.
4. **Avoid introducing unused code** or unnecessary abstractions.
5. **Respect existing naming and module patterns** unless refactoring explicitly.

Whenever in doubt, Copilot should produce:

- Clear, small, and well-documented functions.
- Changes that can be described with a concise, conventional commit message.
- Updates that keep the README and project structure aligned with the current state of the code.
