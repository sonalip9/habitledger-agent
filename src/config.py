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

import logging
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


def get_adk_model_name() -> str:
    """
    Get the model name to be used by the ADK HabitLedger agent.

    Reads from the GOOGLE_ADK_MODEL environment variable if set,
    otherwise falls back to a sensible default (gemini-2.0-flash-exp).

    Returns:
        str: The ADK model name to use.

    Example:
        >>> model = get_adk_model_name()
        >>> print(model)
        gemini-2.0-flash-exp
    """
    return os.getenv("GOOGLE_ADK_MODEL", "gemini-2.0-flash-exp")


def setup_logging(
    level: str = "INFO", structured: bool = False, console: bool = True
) -> None:
    """
    Configure logging for HabitLedger with observability features.

    Sets up logging with a standard format showing timestamp, level, module, and message.
    Supports structured logging for better observability and metrics collection.
    Call this at application startup to enable logging throughout the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Can also be set via LOG_LEVEL environment variable.
        structured: Whether to use JSON-structured logging for observability (default: False).
                   Can also be set via STRUCTURED_LOGGING=true environment variable.
        console: Whether to log to console (default: True).
                   Can also be set via CONSOLE_LOGGING=true environment variable.

    Example:
        >>> setup_logging()
        >>> # Or with custom level and structured logging
        >>> setup_logging("DEBUG", structured=True)
    """
    log_level = os.getenv("LOG_LEVEL", level).upper()
    use_structured = os.getenv("STRUCTURED_LOGGING", str(structured)).lower() == "true"

    valid_levels = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"}
    if log_level not in valid_levels:
        raise ValueError(
            f"Invalid log level '{log_level}'. Valid levels are: {', '.join(sorted(valid_levels))}."
        )

    # Enhanced format with function name and line number for better debugging
    if use_structured:
        # JSON-like structured format for observability tools
        log_format = (
            "timestamp=%(asctime)s level=%(levelname)s module=%(name)s "
            "function=%(funcName)s line=%(lineno)d message=%(message)s"
        )
    else:
        # Human-readable format
        log_format = (
            "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s"
        )

    # Create console handler for CLI/debugging output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    )

    # Create file handler for persistent logging
    file_handler = logging.FileHandler("habitledger.log")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    )

    # Explicitly set root logger level before configuring handlers
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))

    console_logging = os.getenv("CONSOLE_LOGGING", str(console)).lower() == "true"
    logging.basicConfig(
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[console_handler, file_handler] if console_logging else [file_handler],
        force=True,
    )

    # Log startup information
    logger.info(
        "Logging configured",
        extra={
            "log_level": log_level,
            "structured": use_structured,
            "version": "1.0.0",
        },
    )
