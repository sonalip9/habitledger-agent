"""
Tests for configuration functions.

This module tests the configuration utilities including environment detection,
path handling, and API key retrieval.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.config import (
    get_api_key,
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


class TestGetApiKey:
    """Tests for get_api_key function."""

    def test_gets_key_from_env_locally(self):
        """Test gets API key from environment variable locally."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key_local_12345"}):
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            assert get_api_key() == "test_key_local_12345"

    def test_raises_error_when_missing_locally(self):
        """Test raises ValueError with local instructions when key missing."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            os.environ.pop("GOOGLE_API_KEY", None)
            with pytest.raises(ValueError, match="not found in environment variables"):
                get_api_key()

    def test_local_error_message_contains_env_file_instructions(self):
        """Test local error message mentions .env file setup."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            os.environ.pop("GOOGLE_API_KEY", None)
            with pytest.raises(ValueError, match=r"\.env file"):
                get_api_key()

    def test_gets_key_from_kaggle_secrets(self):
        """Test gets API key from Kaggle Secrets when on Kaggle."""
        mock_secrets = MagicMock()
        mock_secrets.get_secret.return_value = "test_key_kaggle_67890"

        with patch.dict(os.environ, {"KAGGLE_KERNEL_RUN_TYPE": "Interactive"}):
            # Mock the module import and class instantiation
            with patch.dict(
                "sys.modules",
                {
                    "kaggle_secrets": MagicMock(
                        UserSecretsClient=MagicMock(return_value=mock_secrets)
                    )
                },
            ):
                assert get_api_key() == "test_key_kaggle_67890"
                mock_secrets.get_secret.assert_called_once_with("GOOGLE_API_KEY")

    def test_fallback_to_env_when_kaggle_secrets_fails(self):
        """Test falls back to environment variable when Kaggle Secrets fails."""
        mock_secrets = MagicMock()
        mock_secrets.get_secret.side_effect = Exception("Secrets API unavailable")

        with patch.dict(
            os.environ,
            {"KAGGLE_KERNEL_RUN_TYPE": "Interactive", "GOOGLE_API_KEY": "fallback_key"},
        ):
            # Mock the module import and class instantiation
            with patch.dict(
                "sys.modules",
                {
                    "kaggle_secrets": MagicMock(
                        UserSecretsClient=MagicMock(return_value=mock_secrets)
                    )
                },
            ):
                assert get_api_key() == "fallback_key"

    def test_raises_error_when_missing_on_kaggle(self):
        """Test raises ValueError with Kaggle instructions when key missing."""
        mock_secrets = MagicMock()
        mock_secrets.get_secret.return_value = None

        with patch.dict(os.environ, {"KAGGLE_KERNEL_RUN_TYPE": "Interactive"}):
            os.environ.pop("GOOGLE_API_KEY", None)
            # Mock the module import and class instantiation
            with patch.dict(
                "sys.modules",
                {
                    "kaggle_secrets": MagicMock(
                        UserSecretsClient=MagicMock(return_value=mock_secrets)
                    )
                },
            ):
                with pytest.raises(ValueError, match="not found in Kaggle Secrets"):
                    get_api_key()

    def test_kaggle_error_message_contains_secrets_instructions(self):
        """Test Kaggle error message mentions Add-ons > Secrets setup."""
        mock_secrets = MagicMock()
        mock_secrets.get_secret.return_value = None

        with patch.dict(os.environ, {"KAGGLE_KERNEL_RUN_TYPE": "Interactive"}):
            os.environ.pop("GOOGLE_API_KEY", None)
            # Mock the module import and class instantiation
            with patch.dict(
                "sys.modules",
                {
                    "kaggle_secrets": MagicMock(
                        UserSecretsClient=MagicMock(return_value=mock_secrets)
                    )
                },
            ):
                with pytest.raises(ValueError, match=r"Add-ons > Secrets"):
                    get_api_key()

    def test_handles_empty_string_from_kaggle_secrets(self):
        """Test treats empty string from Kaggle Secrets as missing key."""
        mock_secrets = MagicMock()
        mock_secrets.get_secret.return_value = ""

        with patch.dict(os.environ, {"KAGGLE_KERNEL_RUN_TYPE": "Interactive"}):
            os.environ.pop("GOOGLE_API_KEY", None)
            # Mock the module import and class instantiation
            with patch.dict(
                "sys.modules",
                {
                    "kaggle_secrets": MagicMock(
                        UserSecretsClient=MagicMock(return_value=mock_secrets)
                    )
                },
            ):
                with pytest.raises(ValueError, match="not found in Kaggle Secrets"):
                    get_api_key()

    def test_handles_empty_string_from_env_locally(self):
        """Test treats empty string from environment as missing key."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": ""}):
            os.environ.pop("KAGGLE_KERNEL_RUN_TYPE", None)
            with pytest.raises(ValueError, match="not found in environment variables"):
                get_api_key()

    def test_kaggle_secrets_import_error_falls_back_to_env(self):
        """Test falls back to env variable when kaggle_secrets module not available."""
        with patch.dict(
            os.environ,
            {"KAGGLE_KERNEL_RUN_TYPE": "Interactive", "GOOGLE_API_KEY": "env_key"},
        ):
            # Simulate import error - kaggle_secrets module not available
            # When the import fails, the try block catches it and falls back to env
            with patch.dict("sys.modules", {"kaggle_secrets": None}):
                assert get_api_key() == "env_key"
