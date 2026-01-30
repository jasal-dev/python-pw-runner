"""Tests for the FastAPI backend."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pw_runner.api import app
from pw_runner.models import ensure_run_dirs, get_run_summary_path


class TestAPI:
    """Tests for the API endpoints."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client."""
        return TestClient(app)

    def test_root_endpoint(self, client: TestClient) -> None:
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Python Playwright Test Runner API"
        assert data["status"] == "running"

    def test_health_endpoint(self, client: TestClient) -> None:
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_list_runs_empty(self, client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test listing runs when there are none."""
        monkeypatch.chdir(tmp_path)
        
        response = client.get("/api/runs")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_run(self, client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test getting a run's status."""
        monkeypatch.chdir(tmp_path)
        
        # Create a fake run on disk
        run_id = "run-20240130-120000-12345678"
        ensure_run_dirs(run_id)
        
        summary_data = {
            "run_id": run_id,
            "start_time": "2024-01-30T12:00:00",
            "status": "completed",
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "tests": []
        }
        
        summary_path = get_run_summary_path(run_id)
        with open(summary_path, "w") as f:
            json.dump(summary_data, f)
        
        # Get the run status
        response = client.get(f"/api/runs/{run_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == run_id
        assert "status" in data
        assert "start_time" in data

    def test_get_nonexistent_run(self, client: TestClient) -> None:
        """Test getting a run that doesn't exist."""
        response = client.get("/api/runs/run-nonexistent")
        assert response.status_code == 404

    def test_list_runs(self, client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test listing multiple runs."""
        monkeypatch.chdir(tmp_path)
        
        # Create two fake runs
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
        response = client.get("/api/runs")
        assert response.status_code == 200
        runs = response.json()
        assert len(runs) == 2
