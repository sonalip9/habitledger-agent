"""
Tests for configuration functions.

This module tests the configuration utilities including environment detection,
path handling, and API key retrieval.
"""

import os
from pathlib import Path
from unittest.mock import patch

from src.config import (
    get_data_path,
    get_working_directory,
    is_kaggle_environment,
    load_env,
)


class TestIsKaggleEnvironment:
    """Tests for is_kaggle_environment function."""

    def test_returns_false_when_not_on_kaggle(self):
        """Test returns False when KAGGLE_KERNEL_RUN_TYPE is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove the env var if it exists
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            assert is_kaggle_environment() is False

    def test_returns_true_when_on_kaggle(self):
        """Test returns True when KAGGLE_KERNEL_RUN_TYPE is set."""
        with patch.dict(os.environ, {"KAGGLE_KERNEL_RUN_TYPE": "Interactive"}):
            assert is_kaggle_environment() is True

    def test_returns_true_for_any_kernel_type(self):
        """Test returns True for any KAGGLE_KERNEL_RUN_TYPE value."""
        with patch.dict(os.environ, {"KAGGLE_KERNEL_RUN_TYPE": "Batch"}):
            assert is_kaggle_environment() is True


class TestGetDataPath:
    """Tests for get_data_path function."""

    def test_returns_local_path_when_not_on_kaggle(self):
        """Test returns local data path when not on Kaggle."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            path = get_data_path("behaviour_principles.json")
            assert "data" in path
            assert "behaviour_principles.json" in path

    def test_returns_path_object_convertible_to_string(self):
        """Test returned path can be used as a string."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            path = get_data_path()
            assert isinstance(path, str)

    def test_uses_default_filename(self):
        """Test uses default behaviour_principles.json filename."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            path = get_data_path()
            assert "behaviour_principles.json" in path


class TestGetWorkingDirectory:
    """Tests for get_working_directory function."""

    def test_returns_cwd_when_not_on_kaggle(self):
        """Test returns current working directory when not on Kaggle."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            working_dir = get_working_directory()
            assert working_dir == Path.cwd()

    def test_returns_kaggle_working_when_on_kaggle(self):
        """Test returns /kaggle/working when on Kaggle."""
        with patch.dict(os.environ, {"KAGGLE_KERNEL_RUN_TYPE": "Interactive"}):
            working_dir = get_working_directory()
            assert working_dir == Path("/kaggle/working")

    def test_returns_path_object(self):
        """Test returns a Path object."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            working_dir = get_working_directory()
            assert isinstance(working_dir, Path)


class TestLoadEnv:
    """Tests for load_env function."""

    def test_load_env_succeeds_locally(self):
        """Test load_env runs without error in local environment."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            # Should not raise
            load_env()

    def test_load_env_is_noop_on_kaggle(self):
        """Test load_env does nothing on Kaggle."""
        with patch.dict(os.environ, {"KAGGLE_KERNEL_RUN_TYPE": "Interactive"}):
            # Should not raise
            load_env()
