"""Tests for the core data model and helper functions."""

import re
from pathlib import Path

import pytest

from pw_runner.models import (
    ensure_run_dirs,
    ensure_test_dirs,
    generate_run_id,
    get_artifact_root,
    get_events_path,
    get_run_dir,
    get_run_summary_path,
    get_test_dir,
    get_trace_path,
    sanitize_nodeid,
)


class TestGenerateRunId:
    """Tests for run ID generation."""

    def test_run_id_format(self) -> None:
        """Test that generated run IDs match the expected format."""
        run_id = generate_run_id()
        # Format: run-YYYYMMDD-HHMMSS-xxxxxxxx
        pattern = r"^run-\d{8}-\d{6}-[a-f0-9]{8}$"
        assert re.match(pattern, run_id), f"Run ID {run_id} doesn't match expected format"

    def test_run_id_uniqueness(self) -> None:
        """Test that multiple calls generate unique run IDs."""
        run_ids = [generate_run_id() for _ in range(10)]
        assert len(set(run_ids)) == 10, "Generated run IDs are not unique"

    def test_run_id_starts_with_run(self) -> None:
        """Test that run IDs start with 'run-' prefix."""
        run_id = generate_run_id()
        assert run_id.startswith("run-"), "Run ID should start with 'run-'"


class TestSanitizeNodeid:
    """Tests for nodeid sanitization."""

    def test_simple_function_test(self) -> None:
        """Test sanitization of a simple function test."""
        nodeid = "tests/test_login.py::test_valid_user"
        expected = "tests_test_login_py__test_valid_user"
        assert sanitize_nodeid(nodeid) == expected

    def test_class_method_test(self) -> None:
        """Test sanitization of a class method test."""
        nodeid = "tests/test_login.py::TestLogin::test_valid_user"
        expected = "tests_test_login_py__TestLogin__test_valid_user"
        assert sanitize_nodeid(nodeid) == expected

    def test_nested_path(self) -> None:
        """Test sanitization of tests in nested directories."""
        nodeid = "tests/auth/oauth/test_google.py::test_login"
        expected = "tests_auth_oauth_test_google_py__test_login"
        assert sanitize_nodeid(nodeid) == expected

    def test_parametrized_test(self) -> None:
        """Test sanitization of parametrized tests."""
        nodeid = "test_app.py::TestCart::test_add[item-1]"
        expected = "test_app_py__TestCart__test_add_item-1_"
        assert sanitize_nodeid(nodeid) == expected

    def test_removes_unsafe_characters(self) -> None:
        """Test that unsafe filesystem characters are removed."""
        nodeid = 'test_file.py::test_with<unsafe>chars|here'
        result = sanitize_nodeid(nodeid)
        # Should not contain unsafe characters
        unsafe_chars = '<>:"|?*[]'
        for char in unsafe_chars:
            assert char not in result, f"Unsafe character '{char}' found in sanitized nodeid"

    def test_collapses_multiple_underscores(self) -> None:
        """Test that multiple consecutive underscores are collapsed."""
        nodeid = "test__file.py::test___method"
        result = sanitize_nodeid(nodeid)
        assert "___" not in result, "Multiple underscores should be collapsed"
        assert "__" in result, "Double underscores from :: should remain"

    def test_windows_path_separator(self) -> None:
        """Test that Windows path separators are handled."""
        nodeid = r"tests\auth\test_login.py::test_valid"
        expected = "tests_auth_test_login_py__test_valid"
        assert sanitize_nodeid(nodeid) == expected


class TestPathHelpers:
    """Tests for path helper functions."""

    def test_get_artifact_root(self) -> None:
        """Test artifact root path construction."""
        root = get_artifact_root()
        assert isinstance(root, Path)
        assert root.name == "runs"
        assert root.parent.name == ".pw-runner"

    def test_get_run_dir(self) -> None:
        """Test run directory path construction."""
        run_id = "run-20240130-150422-a1b2c3d4"
        run_dir = get_run_dir(run_id)
        assert isinstance(run_dir, Path)
        assert run_dir.name == run_id
        assert run_dir.parent.name == "runs"

    def test_get_test_dir(self) -> None:
        """Test test directory path construction."""
        run_id = "run-20240130-150422-a1b2c3d4"
        nodeid = "tests/test_login.py::test_valid"
        test_dir = get_test_dir(run_id, nodeid)
        assert isinstance(test_dir, Path)
        assert test_dir.name == "tests_test_login_py__test_valid"
        assert test_dir.parent.name == "tests"

    def test_get_trace_path(self) -> None:
        """Test trace file path construction."""
        run_id = "run-20240130-150422-a1b2c3d4"
        nodeid = "tests/test_login.py::test_valid"
        trace_path = get_trace_path(run_id, nodeid)
        assert isinstance(trace_path, Path)
        assert trace_path.name == "trace.zip"
        assert "tests_test_login_py__test_valid" in str(trace_path)

    def test_get_run_summary_path(self) -> None:
        """Test run summary path construction."""
        run_id = "run-20240130-150422-a1b2c3d4"
        summary_path = get_run_summary_path(run_id)
        assert isinstance(summary_path, Path)
        assert summary_path.name == "run-summary.json"
        assert run_id in str(summary_path)

    def test_get_events_path(self) -> None:
        """Test events file path construction."""
        run_id = "run-20240130-150422-a1b2c3d4"
        events_path = get_events_path(run_id)
        assert isinstance(events_path, Path)
        assert events_path.name == "events.ndjson"
        assert run_id in str(events_path)


class TestDirectoryCreation:
    """Tests for directory creation helpers."""

    def test_ensure_run_dirs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that run directory structure is created correctly."""
        # Use tmp_path as the working directory
        monkeypatch.chdir(tmp_path)
        
        run_id = "run-20240130-150422-a1b2c3d4"
        run_dir = ensure_run_dirs(run_id)
        
        assert run_dir.exists()
        assert run_dir.is_dir()
        assert (run_dir / "tests").exists()
        assert (run_dir / "tests").is_dir()

    def test_ensure_test_dirs(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that test directory structure is created correctly."""
        # Use tmp_path as the working directory
        monkeypatch.chdir(tmp_path)
        
        run_id = "run-20240130-150422-a1b2c3d4"
        nodeid = "tests/test_login.py::test_valid"
        test_dir = ensure_test_dirs(run_id, nodeid)
        
        assert test_dir.exists()
        assert test_dir.is_dir()
        assert test_dir.name == "tests_test_login_py__test_valid"

    def test_ensure_dirs_idempotent(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test that calling ensure_dirs multiple times is safe."""
        # Use tmp_path as the working directory
        monkeypatch.chdir(tmp_path)
        
        run_id = "run-20240130-150422-a1b2c3d4"
        
        # Call twice
        run_dir1 = ensure_run_dirs(run_id)
        run_dir2 = ensure_run_dirs(run_id)
        
        assert run_dir1 == run_dir2
        assert run_dir1.exists()

    def test_ensure_test_dirs_creates_parent(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that ensure_test_dirs creates parent directories."""
        # Use tmp_path as the working directory
        monkeypatch.chdir(tmp_path)
        
        run_id = "run-20240130-150422-a1b2c3d4"
        nodeid = "tests/test_login.py::test_valid"
        
        # Don't create run dir first - ensure_test_dirs should handle it
        test_dir = ensure_test_dirs(run_id, nodeid)
        
        assert test_dir.exists()
        assert get_run_dir(run_id).exists()
        assert (get_run_dir(run_id) / "tests").exists()
