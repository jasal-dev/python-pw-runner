"""Test discovery using pytest's collection mechanism."""

import json
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class DiscoveredTest:
    """Information about a discovered test."""
    nodeid: str
    file_path: str
    class_name: Optional[str]
    function_name: str
    markers: list[str]


def discover_tests(
    path: Optional[str] = None,
    keyword: Optional[str] = None,
    marker: Optional[str] = None,
    timeout: int = 60
) -> list[DiscoveredTest]:
    """Discover tests using pytest's collection mechanism.
    
    Args:
        path: Optional path to limit test discovery.
        keyword: Optional keyword filter.
        marker: Optional marker filter.
        timeout: Timeout in seconds for test collection (default: 60).
        
    Returns:
        List of discovered tests.
        
    Raises:
        RuntimeError: If test discovery times out or fails.
    """
    # Build pytest command for collection
    cmd = ["pytest", "--collect-only", "-q", "--no-header"]
    
    if path:
        cmd.append(path)
    
    if keyword:
        cmd.extend(["-k", keyword])
    
    if marker:
        cmd.extend(["-m", marker])
    
    # Add JSON output option using a custom plugin approach
    # For MVP, we'll parse the regular output
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        
        # Parse the output
        tests = []
        for line in result.stdout.splitlines():
            line = line.strip()
            if "::" in line and "<" in line:
                # Line format: <Module path/to/test.py>
                # or: <Function test_name>
                # We need the nodeid format instead
                continue
            elif "::" in line:
                # This is a nodeid
                nodeid = line
                # Parse nodeid to extract components
                test_info = _parse_nodeid(nodeid)
                if test_info:
                    tests.append(test_info)
        
        return tests
    
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"Test discovery timed out after {timeout} seconds. "
            "Consider reducing the number of tests or increasing the timeout."
        )
    except Exception as e:
        raise RuntimeError(f"Test discovery failed: {e}")


def _parse_nodeid(nodeid: str) -> Optional[DiscoveredTest]:
    """Parse a pytest nodeid into test information.
    
    Args:
        nodeid: The pytest nodeid (e.g., "tests/test_login.py::TestLogin::test_valid").
        
    Returns:
        DiscoveredTest object or None if parsing fails.
    """
    if "::" not in nodeid:
        return None
    
    parts = nodeid.split("::")
    file_path = parts[0]
    
    # Determine class and function names
    if len(parts) == 2:
        # Format: file::function
        class_name = None
        function_name = parts[1]
    elif len(parts) == 3:
        # Format: file::class::function
        class_name = parts[1]
        function_name = parts[2]
    else:
        # Unexpected format
        return None
    
    # For MVP, markers are empty (would need pytest collection JSON for this)
    markers: list[str] = []
    
    return DiscoveredTest(
        nodeid=nodeid,
        file_path=file_path,
        class_name=class_name,
        function_name=function_name,
        markers=markers,
    )


def group_tests_by_file(tests: list[DiscoveredTest]) -> dict[str, list[DiscoveredTest]]:
    """Group tests by their file path.
    
    Args:
        tests: List of test information.
        
    Returns:
        Dictionary mapping file paths to lists of tests.
    """
    grouped: dict[str, list[DiscoveredTest]] = {}
    for test in tests:
        if test.file_path not in grouped:
            grouped[test.file_path] = []
        grouped[test.file_path].append(test)
    return grouped
