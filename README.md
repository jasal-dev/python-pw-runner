# Python Playwright Test Runner

A local graphical test runner for Python + pytest + Playwright, inspired by the Playwright JavaScript test runner experience.

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/jasal-dev/python-pw-runner.git
cd python-pw-runner

# Install the package
pip install -e .

# Install Playwright browsers
playwright install chromium
```

### Running the Test Runner

Start the backend server:

```bash
pw-runner
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` to see the interactive API documentation.

### Using the API

**Discover tests:**
```bash
curl http://localhost:8000/api/tests
```

**Start a test run:**
```bash
curl -X POST http://localhost:8000/api/runs \
  -H "Content-Type: application/json" \
  -d '{"test_nodeids": ["examples/saucedemo/test_saucedemo.py::test_valid_login"]}'
```

**Get run status:**
```bash
curl http://localhost:8000/api/runs/<run-id>
```

**List all runs:**
```bash
curl http://localhost:8000/api/runs
```

### Running Example Tests

The repository includes example tests for the [Sauce Labs demo site](https://www.saucedemo.com/):

```bash
# Run all example tests
pytest examples/saucedemo/ -v

# Run with the test runner (captures traces)
pytest examples/saucedemo/ -v --pw-runner-run-id=example-run

# View traces
playwright show-trace .pw-runner/runs/example-run/tests/<test-name>/trace.zip
```

See [examples/saucedemo/README.md](examples/saucedemo/README.md) for more details.

## Project Purpose and Goals

This project aims to provide a modern, user-friendly graphical interface for running Python-based Playwright tests. The goal is to bring the excellent developer experience of the Playwright JavaScript test runner to the Python ecosystem.

**Key Goals:**
- **Visual Test Selection**: Browse and select tests through an intuitive web UI
- **Live Progress Tracking**: Monitor test execution in real-time with streaming updates
- **Artifact Management**: Automatically capture and organize test artifacts, including Playwright traces
- **Developer Experience**: Simplify the local testing workflow for Playwright Python users

## High-Level Architecture

The Python Playwright Test Runner follows a client-server architecture with two main components:

### Backend (Test Runner Engine)

The backend is responsible for test discovery, execution, and event streaming:

- **Framework**: FastAPI web server for REST API and WebSocket support
- **Test Execution**: Launches pytest as a subprocess to run selected tests
- **Event Streaming**: Real-time updates via WebSocket/SSE for test progress and results
- **Artifact Collection**: Manages per-run and per-test artifact directories
- **Trace Capture**: Ensures Playwright traces are always captured during test execution

Key responsibilities:
- Discover available tests from the test suite
- Execute pytest with appropriate configuration
- Stream live test events (start, pass, fail, skip)
- Collect and organize artifacts (traces, screenshots, videos)
- Serve artifact metadata to the frontend

### Frontend (Web UI)

The frontend provides an interactive web-based user interface:

- **Test Browser**: Navigate and select tests to run
- **Live Progress**: Real-time test execution status and progress bars
- **Artifact Viewer**: Browse and access captured artifacts
- **Results Dashboard**: Summary of test runs with pass/fail statistics

Key features:
- Select individual tests or test suites
- View streaming test results as they execute
- Access links to artifacts (traces, screenshots, videos)
- Filter and search tests

## Artifact and Trace Management

### Artifact Directory Structure

The runner organizes artifacts in a clear hierarchy:

```
artifacts/
├── run-<timestamp>/
│   ├── test-<test-name>/
│   │   ├── trace.zip
│   │   ├── screenshots/
│   │   └── videos/
│   ├── test-<another-test>/
│   │   └── trace.zip
│   └── run-summary.json
```

### Trace Capture

**Always-On Tracing**: The runner configures pytest and Playwright to capture traces for every test execution, ensuring debugging information is always available when tests fail.

**Viewing Traces**: Traces are saved as `.zip` files and can be opened using the Playwright CLI:

```bash
playwright show-trace artifacts/run-<timestamp>/test-<name>/trace.zip
```

The web UI provides convenient links to trace files, making it easy to download and open them locally.

## Related Work and Issues

This project is being developed incrementally. Key features and components are tracked in the following GitHub issues:

- [#1](https://github.com/jasal-dev/python-pw-runner/issues/1) - ✅ Initial project setup and planning
- [#2](https://github.com/jasal-dev/python-pw-runner/issues/2) - ✅ Backend API design
- [#3](https://github.com/jasal-dev/python-pw-runner/issues/3) - ✅ Test discovery implementation
- [#4](https://github.com/jasal-dev/python-pw-runner/issues/4) - 🚧 Test execution engine
- [#5](https://github.com/jasal-dev/python-pw-runner/issues/5) - ✅ Event streaming infrastructure
- [#7](https://github.com/jasal-dev/python-pw-runner/issues/7) - 🚧 Frontend UI development
- [#8](https://github.com/jasal-dev/python-pw-runner/issues/8) - ⏳ Artifact management
- [#9](https://github.com/jasal-dev/python-pw-runner/issues/9) - ✅ Trace capture integration

## Implementation Status

### ✅ Completed Features

- **Data Model** - Run IDs, artifact directory structure, path sanitization
- **Backend API** - FastAPI server with REST endpoints
- **Test Discovery** - pytest collection with filtering (path, keyword, marker)
- **Run Management** - Start, monitor, and cancel test runs
- **Event Streaming** - Custom pytest plugin for structured event emission
- **Trace Capture** - Automatic Playwright trace recording per test
- **Example Tests** - saucedemo.com demo test suite
- **CLI** - `pw-runner` command to start the server

### 🚧 In Progress

- **Frontend UI** - Web interface for test selection and monitoring (Issue #8)

### ⏳ Future Enhancements

- **WebSocket streaming** - Real-time event push to frontend
- **Test filtering UI** - Advanced search and filter capabilities
- **Trace viewer integration** - In-browser trace viewing
- **CI/CD integration** - GitHub Actions, GitLab CI support
- **Test parallelization** - Built-in parallel execution

## API Documentation

The backend provides a RESTful API with the following endpoints:

### Test Discovery

- `GET /api/tests` - Discover available tests
  - Query params: `path`, `keyword`, `marker`
  - Returns: List of tests with metadata, grouped by file

### Run Management

- `POST /api/runs` - Start a new test run
  - Body: `{"test_nodeids": ["test1", "test2"], "pytest_args": ["-v"]}`
  - Returns: `{"run_id": "run-...", "status": "running"}`

- `GET /api/runs` - List all test runs
  - Returns: Array of run summaries

- `GET /api/runs/{run_id}` - Get run details
  - Returns: Run summary with test results

- `DELETE /api/runs/{run_id}` - Cancel a running test
  - Returns: Status message

### Artifacts

- `GET /artifacts/{run_id}/tests/{test_name}/trace.zip` - Download trace file
- `GET /artifacts/{run_id}/run-summary.json` - Download run summary
- `GET /artifacts/{run_id}/events.ndjson` - Download event stream

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest tests/ --cov=pw_runner --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

### Project Structure

```
python-pw-runner/
├── src/pw_runner/          # Main package
│   ├── __init__.py
│   ├── api.py             # FastAPI application
│   ├── cli.py             # Command-line interface
│   ├── models.py          # Data models and utilities
│   ├── runner.py          # Test run manager
│   ├── discovery.py       # Test discovery
│   ├── pytest_plugin.py   # Event streaming plugin
│   └── fixtures.py        # Playwright fixtures
├── tests/                 # Unit tests
├── examples/saucedemo/    # Example test suite
├── docs/                  # Documentation
└── README.md
```

## MVP Scope

### In Scope for MVP

The Minimum Viable Product focuses on core local testing workflows:

- ✅ **Web-based UI** for test selection and monitoring
- ✅ **Backend API** (FastAPI) for test management
- ✅ **Test discovery** from pytest/Playwright test suites
- ✅ **Test execution** via pytest subprocess
- ✅ **Live progress updates** via event streaming
- ✅ **Artifact collection** with organized directory structure
- ✅ **Automatic trace capture** for all test runs
- ✅ **Basic result reporting** (pass/fail/skip counts)

### Non-Goals (Out of Scope for MVP)

To keep the MVP focused and achievable, the following features are explicitly out of scope:

- ❌ **Remote test execution** - MVP runs tests locally only
- ❌ **Built-in parallelism** - Relies on pytest's native parallel execution (pytest-xdist)
- ❌ **In-app trace viewer** - Uses external `playwright show-trace` command
- ❌ **Video playback in browser** - Artifacts are downloaded and viewed locally
- ❌ **Test authoring/editing** - Use your preferred IDE/editor
- ❌ **CI/CD integration** - Focused on local development workflow
- ❌ **User authentication** - Single-user local tool
- ❌ **Historical test analytics** - Shows current run only

## License

This project is currently in early development. License information will be added in a future update.