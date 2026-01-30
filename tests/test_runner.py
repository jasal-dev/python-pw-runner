"""Tests for the run manager."""

import json
from pathlib import Path

import pytest

from pw_runner.models import get_run_summary_path
from pw_runner.runner import RunManager, RunStatus, RunSummary


class TestRunManager:
    """Tests for the RunManager class."""

    @pytest.fixture
    def manager(self) -> RunManager:
        """Create a fresh run manager for each test."""
        return RunManager()

    def test_initial_state(self, manager: RunManager) -> None:
        """Test that manager starts with no active runs."""
        assert manager.current_run_id is None
        assert not manager.is_running

    def test_list_runs_empty(self, manager: RunManager, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test listing runs when there are none."""
        monkeypatch.chdir(tmp_path)
        
        runs = manager.list_runs()
        assert isinstance(runs, list)
        assert len(runs) == 0

    def test_get_run_summary_from_disk(
        self, manager: RunManager, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading run summary from disk."""
        monkeypatch.chdir(tmp_path)
        
        # Create a fake run summary on disk
        from pw_runner.models import ensure_run_dirs
        
        run_id = "run-20240130-120000-12345678"
        ensure_run_dirs(run_id)
        
        summary_data = {
            "run_id": run_id,
            "start_time": "2024-01-30T12:00:00",
            "end_time": "2024-01-30T12:01:00",
            "duration_seconds": 60.0,
            "status": "completed",
            "total_tests": 5,
            "passed": 4,
            "failed": 1,
            "skipped": 0,
            "tests": []
        }
        
        summary_path = get_run_summary_path(run_id)
        with open(summary_path, "w") as f:
            json.dump(summary_data, f)
        
        # Load the summary
        summary = manager.get_run_summary(run_id)
        
        assert summary is not None
        assert summary.run_id == run_id
        assert summary.status == RunStatus.COMPLETED
        assert summary.total_tests == 5
        assert summary.passed == 4

    def test_list_runs_from_disk(
        self, manager: RunManager, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test listing runs from disk."""
        monkeypatch.chdir(tmp_path)
        
        # Create two fake run summaries
        from pw_runner.models import ensure_run_dirs
        
        runs_data = [
            {
                "run_id": "run-20240130-120000-12345678",
                "start_time": "2024-01-30T12:00:00",
                "status": "completed",
            },
            {
                "run_id": "run-20240130-130000-87654321",
                "start_time": "2024-01-30T13:00:00",
                "status": "completed",
            }
        ]
        
        for run_data in runs_data:
            run_id = run_data["run_id"]
            ensure_run_dirs(run_id)
            
            summary_data = {
                **run_data,
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "tests": []
            }
            
            summary_path = get_run_summary_path(run_id)
            with open(summary_path, "w") as f:
                json.dump(summary_data, f)
        
        # List runs
        runs = manager.list_runs()
        
        assert len(runs) == 2
        # Should be sorted by start time, newest first
        assert runs[0].run_id == "run-20240130-130000-87654321"
        assert runs[1].run_id == "run-20240130-120000-12345678"
