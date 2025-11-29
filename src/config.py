"""
Configuration & API key loading.

This module manages configuration and API keys for the HabitLedger agent.
It handles loading environment variables from .env files and provides
access to configuration values needed throughout the application.

The module follows these principles:
- Single responsibility: Only handles configuration management
- DRY: Centralizes all configuration logic in one place
- Explicit errors: Raises clear exceptions when required config is missing
- Environment compatibility: Works on both Kaggle and local environments
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv


def is_kaggle_environment() -> bool:
    """
    Check if code is running in a Kaggle notebook environment.

    This function detects the Kaggle environment by checking for
    the KAGGLE_KERNEL_RUN_TYPE environment variable which is set
    by Kaggle for all notebook kernels.

    Returns:
        bool: True if running on Kaggle, False otherwise.

    Example:
        >>> if is_kaggle_environment():
        ...     print("Running on Kaggle")
        ... else:
        ...     print("Running locally")
    """
    return os.getenv("KAGGLE_KERNEL_RUN_TYPE") is not None


def get_data_path(filename: str = "behaviour_principles.json") -> str:
    """
    Get the appropriate path to data files based on the environment.

    On Kaggle, data files are expected to be in /kaggle/input/habitledger-agent/data/
    (when the repository is uploaded as a Kaggle Dataset). On local environments, the
    standard data/ directory relative to the project root is used.

    The function tries multiple fallback locations on Kaggle:
    1. /kaggle/input/habitledger-agent/data/ (recommended)
    2. /kaggle/input/habitledger-data/ (legacy)
    3. /kaggle/working/ (embedded data)
    Args:
        filename: Name of the data file (default: "behaviour_principles.json").

    Returns:
        str: Full path to the data file.

    Example:
        >>> db_path = get_data_path("behaviour_principles.json")
        >>> behaviour_db = load_behaviour_db(db_path)
    """
    if is_kaggle_environment():
        # On Kaggle, data is in /kaggle/input/{dataset-name}/
        # Try habitledger-agent dataset first (recommended setup)
        kaggle_data_path = Path("/kaggle/input/habitledger-agent/data") / filename
        if kaggle_data_path.exists():
            return str(kaggle_data_path)
        # Fallback to habitledger-data dataset (legacy)
        kaggle_data_path = Path("/kaggle/input/habitledger-data") / filename
        if kaggle_data_path.exists():
            return str(kaggle_data_path)
        # Fallback to working directory if data is embedded
        working_path = Path("/kaggle/working") / filename
        if working_path.exists():
            return str(working_path)

    # No valid path found on Kaggle: raise explicit error
    if is_kaggle_environment():
        raise FileNotFoundError(
            f"Data file '{filename}' not found in Kaggle environment. "
            f"Please ensure the habitledger-agent dataset is attached to your notebook. "
            f"See docs/KAGGLE_INSTRUCTIONS.md for setup instructions."
        )

    # Local environment: use relative path from src/ to data/
    local_path = Path(__file__).parent.parent / "data" / filename
    return str(local_path)


def get_working_directory() -> Path:
    """
    Get the appropriate working directory for file output based on environment.

    On Kaggle, writes should go to /kaggle/working/ which persists during
    the notebook session. On local environments, uses the current working
    directory or the project root.

    Returns:
        Path: Path to the working directory for file output.

    Example:
        >>> working_dir = get_working_directory()
        >>> output_file = working_dir / "user_memory.json"
    """
    if is_kaggle_environment():
        return Path("/kaggle/working")
    return Path.cwd()


def load_env() -> None:
    """
    Load environment variables from .env file.

    This function should be called once at application startup to load
    all environment variables from the .env file in the project root.
    It searches for .env file in the current directory and parent directories.

    On Kaggle, this function is a no-op since environment variables
    are managed through Kaggle Secrets.

    Returns:
        None

    Note:
        This function is idempotent - calling it multiple times is safe.
        Existing environment variables will not be overwritten.
    """
    # Skip loading .env on Kaggle (use Kaggle Secrets instead)
    if is_kaggle_environment():
        return

    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)


def get_api_key() -> str:
    """
    Retrieve the Google API key from environment variables or Kaggle Secrets.

    On Kaggle, this function uses the Kaggle Secrets API to retrieve the
    GOOGLE_API_KEY secret. On local environments, it reads from the
    GOOGLE_API_KEY environment variable (typically set via .env file).

    Returns:
        str: The Google API key.

    Raises:
        ValueError: If GOOGLE_API_KEY is not set in environment variables
                   or Kaggle Secrets.

    Example:
        >>> api_key = get_api_key()
        >>> print(f"API key loaded: {api_key[:10]}...")
    """
    # Try Kaggle Secrets first if on Kaggle
    if is_kaggle_environment():
        try:
            from kaggle_secrets import UserSecretsClient  # type: ignore # pylint: disable=import-error

            user_secrets = UserSecretsClient()
            api_key = user_secrets.get_secret("GOOGLE_API_KEY")
            if api_key:
                return api_key
        except Exception:  # noqa: BLE001
            # Fall through to environment variable check
            pass

    # Try environment variable
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        if is_kaggle_environment():
            raise ValueError(
                "GOOGLE_API_KEY not found in Kaggle Secrets. "
                "Please add it via: Add-ons > Secrets > Add a new secret. "
                "Use 'GOOGLE_API_KEY' as the label and your API key as the value."
            )
        else:
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
    otherwise falls back to gemini-1.5-flash which has better quota limits.

    Returns:
        str: The ADK model name to use.

    Example:
        >>> model = get_adk_model_name()
        >>> print(model)
        gemini-1.5-flash

    Note:
        gemini-1.5-flash is recommended for production as it has:
        - Higher quota limits on free tier
        - Better reliability and stability
        - Lower rate of quota exhaustion

        gemini-2.0-flash-exp is experimental and has stricter quotas.
    """
    return os.getenv("GOOGLE_ADK_MODEL", "gemini-1.5-flash")


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
