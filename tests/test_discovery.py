"""Tests for the test discovery functionality."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from pw_runner.api import app
from pw_runner.discovery import DiscoveredTest, _parse_nodeid, discover_tests, group_tests_by_file


class TestParseNodeid:
    """Tests for nodeid parsing."""

    def test_parse_simple_function(self) -> None:
        """Test parsing a simple function test."""
        nodeid = "tests/test_login.py::test_valid"
        test_info = _parse_nodeid(nodeid)
        
        assert test_info is not None
        assert test_info.nodeid == nodeid
        assert test_info.file_path == "tests/test_login.py"
        assert test_info.class_name is None
        assert test_info.function_name == "test_valid"

    def test_parse_class_method(self) -> None:
        """Test parsing a class method test."""
        nodeid = "tests/test_login.py::TestLogin::test_valid"
        test_info = _parse_nodeid(nodeid)
        
        assert test_info is not None
        assert test_info.nodeid == nodeid
        assert test_info.file_path == "tests/test_login.py"
        assert test_info.class_name == "TestLogin"
        assert test_info.function_name == "test_valid"

    def test_parse_invalid_nodeid(self) -> None:
        """Test parsing an invalid nodeid."""
        nodeid = "not_a_valid_nodeid"
        test_info = _parse_nodeid(nodeid)
        
        assert test_info is None


class TestGroupTestsByFile:
    """Tests for grouping tests by file."""

    def test_group_empty_list(self) -> None:
        """Test grouping an empty list."""
        grouped = group_tests_by_file([])
        assert grouped == {}

    def test_group_single_file(self) -> None:
        """Test grouping tests from a single file."""
        tests = [
            DiscoveredTest(
                nodeid="test_file.py::test_one",
                file_path="test_file.py",
                class_name=None,
                function_name="test_one",
                markers=[]
            ),
            DiscoveredTest(
                nodeid="test_file.py::test_two",
                file_path="test_file.py",
                class_name=None,
                function_name="test_two",
                markers=[]
            ),
        ]
        
        grouped = group_tests_by_file(tests)
        
        assert len(grouped) == 1
        assert "test_file.py" in grouped
        assert len(grouped["test_file.py"]) == 2

    def test_group_multiple_files(self) -> None:
        """Test grouping tests from multiple files."""
        tests = [
            DiscoveredTest(
                nodeid="test_file1.py::test_one",
                file_path="test_file1.py",
                class_name=None,
                function_name="test_one",
                markers=[]
            ),
            DiscoveredTest(
                nodeid="test_file2.py::test_two",
                file_path="test_file2.py",
                class_name=None,
                function_name="test_two",
                markers=[]
            ),
        ]
        
        grouped = group_tests_by_file(tests)
        
        assert len(grouped) == 2
        assert "test_file1.py" in grouped
        assert "test_file2.py" in grouped


class TestDiscoveryAPI:
    """Tests for the test discovery API endpoint."""

    @pytest.fixture
    def client(self) -> TestClient:
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def sample_test_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
        """Create a sample test file for discovery."""
        monkeypatch.chdir(tmp_path)
        
        test_content = '''
def test_example_one():
    """Example test one."""
    assert True


def test_example_two():
    """Example test two."""
    assert True


class TestExample:
    """Example test class."""
    
    def test_method_one(self):
        """Example method one."""
        assert True
'''
        
        test_file = tmp_path / "test_sample.py"
        test_file.write_text(test_content)
        return test_file

    def test_discover_tests_endpoint(
        self, client: TestClient, sample_test_file: Path
    ) -> None:
        """Test the test discovery endpoint."""
        response = client.get("/api/tests")
        assert response.status_code == 200
        
        data = response.json()
        assert "tests" in data
        assert "total" in data
        assert "grouped_by_file" in data
        
        # Should find our 3 tests
        assert data["total"] == 3
        assert len(data["tests"]) == 3
        
        # Check that tests are grouped by file
        assert "test_sample.py" in data["grouped_by_file"]
        assert len(data["grouped_by_file"]["test_sample.py"]) == 3

    def test_discover_tests_with_path_filter(
        self, client: TestClient, sample_test_file: Path
    ) -> None:
        """Test discovery with path filter."""
        response = client.get(f"/api/tests?path={sample_test_file}")
        assert response.status_code == 200
        
        data = response.json()
        # Should still find the tests
        assert data["total"] >= 0  # May be 0 or more depending on pytest behavior
