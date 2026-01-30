"""Custom pytest plugin for structured event streaming.

This plugin emits structured JSON events during test execution that can be
captured and streamed to the frontend for real-time progress updates.
"""

import json
import sys
from datetime import datetime
from typing import Any, Optional

import pytest


class EventStreamPlugin:
    """Pytest plugin that emits structured events as JSON lines."""
    
    def __init__(self, run_id: str) -> None:
        """Initialize the plugin.
        
        Args:
            run_id: The run ID for this test session.
        """
        self.run_id = run_id
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.skipped_count = 0
    
    def _emit_event(self, event: dict[str, Any]) -> None:
        """Emit a structured event to stdout.
        
        Events are prefixed with 'PW_RUNNER_EVENT:' to distinguish them from
        regular pytest output.
        
        Args:
            event: The event dictionary to emit.
        """
        # Add timestamp if not present
        if "timestamp" not in event:
            event["timestamp"] = datetime.now().isoformat()
        
        # Emit as JSON with prefix
        event_json = json.dumps(event)
        print(f"PW_RUNNER_EVENT:{event_json}", file=sys.stderr, flush=True)
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionstart(self, session: pytest.Session) -> None:
        """Called when the test session starts."""
        self._emit_event({
            "type": "session_start",
            "run_id": self.run_id,
        })
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_logstart(self, nodeid: str, location: tuple[str, Optional[int], str]) -> None:
        """Called when a test starts."""
        self._emit_event({
            "type": "test_start",
            "nodeid": nodeid,
            "location": {
                "file": location[0],
                "line": location[1],
                "name": location[2],
            }
        })
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item: pytest.Item, call: pytest.CallInfo[None]) -> Any:
        """Called when a test phase completes."""
        outcome = yield
        report = outcome.get_result()
        
        # Only emit events for the call phase (not setup/teardown)
        if report.when == "call":
            self._emit_event({
                "type": "test_result",
                "nodeid": item.nodeid,
                "outcome": report.outcome,
                "duration": report.duration,
            })
            
            # Update counts
            if report.outcome == "passed":
                self.passed_count += 1
            elif report.outcome == "failed":
                self.failed_count += 1
            elif report.outcome == "skipped":
                self.skipped_count += 1
    
    @pytest.hookimpl(trylast=True)
    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        """Called when the test session finishes."""
        self._emit_event({
            "type": "session_finish",
            "run_id": self.run_id,
            "passed": self.passed_count,
            "failed": self.failed_count,
            "skipped": self.skipped_count,
            "total": self.passed_count + self.failed_count + self.skipped_count,
            "exit_status": exitstatus,
        })


def pytest_configure(config: pytest.Config) -> None:
    """Register the event stream plugin if run_id is provided."""
    run_id = config.getoption("--pw-runner-run-id", None)
    if run_id:
        plugin = EventStreamPlugin(run_id)
        config.pluginmanager.register(plugin, "pw_runner_events")


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command-line options."""
    parser.addoption(
        "--pw-runner-run-id",
        action="store",
        default=None,
        help="Run ID for event streaming",
    )
