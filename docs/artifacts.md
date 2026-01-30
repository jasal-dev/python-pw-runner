# Artifact Directory Structure and Data Model

## Overview

The Python Playwright Test Runner organizes all test run artifacts in a structured directory hierarchy under `.pw-runner/runs/`. This document describes the data model, directory structure, and file formats.

## Run ID Format

Each test run is assigned a unique `run_id` with the following format:

```
run-<timestamp>-<short-uuid>
```

**Example:** `run-20240130-150422-a1b2c3d4`

- **timestamp**: Date and time when the run started (format: `YYYYMMDD-HHMMSS`)
- **short-uuid**: First 8 characters of a UUID for uniqueness

## Directory Structure

```
.pw-runner/
└── runs/
    └── <run_id>/
        ├── run-summary.json       # Run metadata and results summary
        ├── events.ndjson          # Streaming events (newline-delimited JSON)
        └── tests/
            └── <sanitized_nodeid>/
                ├── trace.zip      # Playwright trace file
                ├── screenshots/   # Optional: test screenshots
                ├── videos/        # Optional: test videos
                └── logs.txt       # Optional: test-specific logs
```

### Example Directory Tree

```
.pw-runner/
└── runs/
    └── run-20240130-150422-a1b2c3d4/
        ├── run-summary.json
        ├── events.ndjson
        └── tests/
            ├── tests_test_login_py__TestLogin__test_valid_user/
            │   ├── trace.zip
            │   └── screenshots/
            └── tests_test_checkout_py__test_purchase_flow/
                └── trace.zip
```

## Test Nodeid Sanitization

Pytest test nodeids follow the format:

```
<path>::<class>::<method>
or
<path>::<function>
```

To create filesystem-safe directory names, nodeids are sanitized using these rules:

1. Replace `/` and `\` with `_`
2. Replace `::` with `__`
3. Replace `.` with `_`
4. Remove or replace unsafe characters: `<>:"|?*[]`
5. Collapse multiple consecutive underscores

**Examples:**

| Original Nodeid | Sanitized Name |
|----------------|----------------|
| `tests/test_login.py::TestLogin::test_valid_user` | `tests_test_login_py__TestLogin__test_valid_user` |
| `tests/auth/test_oauth.py::test_google_login` | `tests_auth_test_oauth_py__test_google_login` |
| `test_app.py::TestCart::test_add[item-1]` | `test_app_py__TestCart__test_add_item-1_` |

## File Formats

### run-summary.json

Contains metadata and results summary for the entire test run.

**Schema:**

```json
{
  "run_id": "run-20240130-150422-a1b2c3d4",
  "start_time": "2024-01-30T15:04:22.123456",
  "end_time": "2024-01-30T15:05:30.654321",
  "duration_seconds": 68.53,
  "status": "completed",
  "total_tests": 15,
  "passed": 12,
  "failed": 2,
  "skipped": 1,
  "tests": [
    {
      "nodeid": "tests/test_login.py::test_valid_user",
      "outcome": "passed",
      "duration_seconds": 2.34,
      "artifacts": {
        "trace": "tests/tests_test_login_py__test_valid_user/trace.zip"
      }
    }
  ]
}
```

**Fields:**

- `run_id`: Unique identifier for this run
- `start_time`: ISO 8601 timestamp when run started
- `end_time`: ISO 8601 timestamp when run completed (null if still running)
- `duration_seconds`: Total run duration in seconds
- `status`: One of `running`, `completed`, `failed`, `cancelled`
- `total_tests`: Total number of tests executed
- `passed`: Number of tests that passed
- `failed`: Number of tests that failed
- `skipped`: Number of tests that were skipped
- `tests`: Array of individual test results

### events.ndjson

Newline-delimited JSON file containing real-time events from the test run. Each line is a complete JSON object representing a single event.

**Event Types:**

1. **Session Start Event**
   ```json
   {"type": "session_start", "timestamp": "2024-01-30T15:04:22.123456", "run_id": "run-..."}
   ```

2. **Test Start Event**
   ```json
   {"type": "test_start", "timestamp": "2024-01-30T15:04:23.456789", "nodeid": "tests/test_login.py::test_valid"}
   ```

3. **Test Result Event**
   ```json
   {"type": "test_result", "timestamp": "2024-01-30T15:04:25.789012", "nodeid": "tests/test_login.py::test_valid", "outcome": "passed", "duration": 2.34}
   ```

4. **Log Event**
   ```json
   {"type": "log", "timestamp": "2024-01-30T15:04:24.123456", "level": "info", "message": "Starting login test"}
   ```

5. **Session Finish Event**
   ```json
   {"type": "session_finish", "timestamp": "2024-01-30T15:05:30.654321", "passed": 12, "failed": 2, "skipped": 1}
   ```

## Helper Functions

The `pw_runner.models` module provides helper functions for working with the artifact structure:

- `generate_run_id()`: Generate a unique run ID
- `sanitize_nodeid(nodeid)`: Convert a nodeid to a safe directory name
- `get_artifact_root()`: Get the root artifact directory path
- `get_run_dir(run_id)`: Get a run's directory path
- `get_test_dir(run_id, nodeid)`: Get a test's directory path
- `get_trace_path(run_id, nodeid)`: Get path to a test's trace file
- `get_run_summary_path(run_id)`: Get path to run summary JSON
- `get_events_path(run_id)`: Get path to events NDJSON file
- `ensure_run_dirs(run_id)`: Create run directory structure
- `ensure_test_dirs(run_id, nodeid)`: Create test directory structure

## Usage Examples

### Creating a New Run

```python
from pw_runner.models import generate_run_id, ensure_run_dirs

# Generate a unique run ID
run_id = generate_run_id()
# => "run-20240130-150422-a1b2c3d4"

# Create the directory structure
run_dir = ensure_run_dirs(run_id)
# Creates: .pw-runner/runs/run-20240130-150422-a1b2c3d4/
```

### Storing Test Artifacts

```python
from pw_runner.models import ensure_test_dirs, get_trace_path

nodeid = "tests/test_login.py::TestLogin::test_valid_user"

# Create test artifact directory
test_dir = ensure_test_dirs(run_id, nodeid)
# Creates: .pw-runner/runs/run-.../tests/tests_test_login_py__TestLogin__test_valid_user/

# Get trace file path
trace_path = get_trace_path(run_id, nodeid)
# => .pw-runner/runs/run-.../tests/tests_test_login_py__TestLogin__test_valid_user/trace.zip
```

### Reading Run Results

```python
import json
from pw_runner.models import get_run_summary_path

summary_path = get_run_summary_path(run_id)
with open(summary_path) as f:
    summary = json.load(f)
    
print(f"Tests passed: {summary['passed']}/{summary['total_tests']}")
```

## Extensibility

The directory structure is designed to be extensible:

1. **Additional artifact types**: Add new files in test directories (e.g., `video.webm`, `coverage.json`)
2. **Custom metadata**: Add fields to `run-summary.json` or create new JSON files
3. **Run-level artifacts**: Store files at the run level (e.g., `pytest.log`, `coverage-report/`)
4. **Event types**: Add new event types to `events.ndjson` as needed

## Best Practices

1. **Always use helper functions**: Use the provided functions in `pw_runner.models` instead of manually constructing paths
2. **Create directories early**: Call `ensure_run_dirs()` and `ensure_test_dirs()` before writing files
3. **Handle concurrent access**: The runner enforces single concurrent runs for MVP, avoiding conflicts
4. **Clean up old runs**: Implement retention policies to manage disk space (future enhancement)
5. **Validate paths**: Always validate that artifact paths exist before attempting to serve them
