"""Core data model and utilities for the Python Playwright Test Runner.

This module defines the data structures and helper functions for managing
test runs, artifacts, and the directory structure used by the runner.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4


def generate_run_id() -> str:
    """Generate a unique run ID.
    
    Format: run-<timestamp>-<short-uuid>
    Example: run-20240130-150422-a1b2c3d4
    
    Returns:
        A unique run identifier string.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    short_uuid = str(uuid4())[:8]
    return f"run-{timestamp}-{short_uuid}"


def sanitize_nodeid(nodeid: str) -> str:
    """Sanitize a pytest nodeid to create a filesystem-safe directory name.
    
    Converts pytest nodeids like 'tests/test_login.py::TestLogin::test_valid_user'
    to safe directory names like 'tests_test_login_py__TestLogin__test_valid_user'
    
    Args:
        nodeid: The pytest test nodeid.
        
    Returns:
        A filesystem-safe string suitable for use as a directory name.
    """
    # First, replace :: with a placeholder to preserve it
    safe_name = nodeid.replace("::", "<!SEPARATOR!>")
    # Replace path separators
    safe_name = safe_name.replace("/", "_").replace("\\", "_")
    # Replace dots
    safe_name = safe_name.replace(".", "_")
    # Remove or replace any remaining unsafe characters
    safe_name = re.sub(r'[<>:"|?*\[\]]', "_", safe_name)
    # Collapse multiple underscores (but not in our placeholder)
    safe_name = re.sub(r'_+', '_', safe_name)
    # Now restore the separator as double underscore
    safe_name = safe_name.replace("_!SEPARATOR!_", "__")
    return safe_name


def get_artifact_root() -> Path:
    """Get the root directory for all test run artifacts.
    
    Returns:
        Path to the artifact root directory (.pw-runner/runs).
    """
    return Path.cwd() / ".pw-runner" / "runs"


def get_run_dir(run_id: str) -> Path:
    """Get the directory path for a specific test run.
    
    Args:
        run_id: The unique run identifier.
        
    Returns:
        Path to the run's artifact directory.
    """
    return get_artifact_root() / run_id


def get_test_dir(run_id: str, nodeid: str) -> Path:
    """Get the directory path for a specific test's artifacts.
    
    Args:
        run_id: The unique run identifier.
        nodeid: The pytest test nodeid.
        
    Returns:
        Path to the test's artifact directory.
    """
    safe_name = sanitize_nodeid(nodeid)
    return get_run_dir(run_id) / "tests" / safe_name


def get_trace_path(run_id: str, nodeid: str) -> Path:
    """Get the path to a test's trace file.
    
    Args:
        run_id: The unique run identifier.
        nodeid: The pytest test nodeid.
        
    Returns:
        Path to the trace.zip file.
    """
    return get_test_dir(run_id, nodeid) / "trace.zip"


def get_run_summary_path(run_id: str) -> Path:
    """Get the path to the run summary JSON file.
    
    Args:
        run_id: The unique run identifier.
        
    Returns:
        Path to the run-summary.json file.
    """
    return get_run_dir(run_id) / "run-summary.json"


def get_events_path(run_id: str) -> Path:
    """Get the path to the run events NDJSON file.
    
    Args:
        run_id: The unique run identifier.
        
    Returns:
        Path to the events.ndjson file.
    """
    return get_run_dir(run_id) / "events.ndjson"


def ensure_run_dirs(run_id: str) -> Path:
    """Create the directory structure for a test run.
    
    Args:
        run_id: The unique run identifier.
        
    Returns:
        Path to the created run directory.
    """
    run_dir = get_run_dir(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "tests").mkdir(exist_ok=True)
    return run_dir


def ensure_test_dirs(run_id: str, nodeid: str) -> Path:
    """Create the directory structure for a specific test.
    
    Args:
        run_id: The unique run identifier.
        nodeid: The pytest test nodeid.
        
    Returns:
        Path to the created test directory.
    """
    test_dir = get_test_dir(run_id, nodeid)
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir
