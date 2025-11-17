"""
Configuration & API key loading.

This module manages configuration and API keys for the HabitLedger agent.
It handles loading environment variables from .env files and provides
access to configuration values needed throughout the application.

The module follows these principles:
- Single responsibility: Only handles configuration management
- DRY: Centralizes all configuration logic in one place
- Explicit errors: Raises clear exceptions when required config is missing
"""

import os
from pathlib import Path

from dotenv import load_dotenv


def load_env() -> None:
    """
    Load environment variables from .env file.

    This function should be called once at application startup to load
    all environment variables from the .env file in the project root.
    It searches for .env file in the current directory and parent directories.

    Returns:
        None

    Note:
        This function is idempotent - calling it multiple times is safe.
        Existing environment variables will not be overwritten.
    """
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)


def get_api_key() -> str:
    """
    Retrieve the Google API key from environment variables.

    Returns:
        str: The Google API key.

    Raises:
        ValueError: If GOOGLE_API_KEY is not set in environment variables.

    Example:
        >>> api_key = get_api_key()
        >>> print(f"API key loaded: {api_key[:10]}...")
    """
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found in environment variables. "
            "Please set it in your .env file or environment. "
            "Example: GOOGLE_API_KEY=your_api_key_here"
        )

    return api_key


def get_model_name() -> str:
    """
    Get the LLM model name to use for the agent.

    Currently returns a hardcoded default model name, but this function
    can be extended to read from environment variables or configuration files.

    Returns:
        str: The model name (e.g., "gpt-4o-mini").

    Note:
        Future enhancement: Make this configurable via environment variable
        MODEL_NAME with this as the fallback default.

    Example:
        >>> model = get_model_name()
        >>> print(model)
        gpt-4o-mini
    """
    # TODO: Make configurable via environment variable
    # return os.getenv("MODEL_NAME", "gpt-4o-mini")
    return "gpt-4o-mini"
