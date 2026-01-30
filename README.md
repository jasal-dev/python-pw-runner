# Python Playwright Test Runner

A local graphical test runner for Python + pytest + Playwright, inspired by the Playwright JavaScript test runner experience.

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

- [#1](https://github.com/jasal-dev/python-pw-runner/issues/1) - Initial project setup and planning
- [#2](https://github.com/jasal-dev/python-pw-runner/issues/2) - Backend API design
- [#3](https://github.com/jasal-dev/python-pw-runner/issues/3) - Test discovery implementation
- [#4](https://github.com/jasal-dev/python-pw-runner/issues/4) - Test execution engine
- [#5](https://github.com/jasal-dev/python-pw-runner/issues/5) - Event streaming infrastructure
- [#7](https://github.com/jasal-dev/python-pw-runner/issues/7) - Frontend UI development
- [#8](https://github.com/jasal-dev/python-pw-runner/issues/8) - Artifact management
- [#9](https://github.com/jasal-dev/python-pw-runner/issues/9) - Trace capture integration

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