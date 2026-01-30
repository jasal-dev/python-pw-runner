"""Run manager for coordinating pytest test execution."""

import asyncio
import json
import subprocess
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field

from pw_runner.models import (
    ensure_run_dirs,
    generate_run_id,
    get_events_path,
    get_run_dir,
    get_run_summary_path,
)


class RunStatus(str, Enum):
    """Status of a test run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TestResult(BaseModel):
    """Result of a single test."""
    nodeid: str
    outcome: str  # passed, failed, skipped, error
    duration_seconds: float
    artifacts: dict[str, str] = Field(default_factory=dict)


class RunSummary(BaseModel):
    """Summary of a test run."""
    run_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    status: RunStatus
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    tests: list[TestResult] = Field(default_factory=list)


class RunManager:
    """Manages test run execution and state.
    
    For MVP, only one concurrent run is allowed.
    """
    
    def __init__(self) -> None:
        """Initialize the run manager."""
        self._current_run: Optional[str] = None
        self._current_process: Optional[asyncio.subprocess.Process] = None
        self._runs: dict[str, RunSummary] = {}
    
    @property
    def current_run_id(self) -> Optional[str]:
        """Get the ID of the currently running test run."""
        return self._current_run
    
    @property
    def is_running(self) -> bool:
        """Check if a test run is currently in progress."""
        return self._current_run is not None
    
    async def start_run(
        self,
        test_nodeids: list[str],
        pytest_args: Optional[list[str]] = None
    ) -> str:
        """Start a new test run.
        
        Args:
            test_nodeids: List of pytest nodeids to run.
            pytest_args: Additional pytest arguments.
            
        Returns:
            The run ID of the started run.
            
        Raises:
            RuntimeError: If a run is already in progress.
        """
        if self.is_running:
            raise RuntimeError("A test run is already in progress")
        
        # Generate run ID and create directories
        run_id = generate_run_id()
        run_dir = ensure_run_dirs(run_id)
        
        # Create run summary
        summary = RunSummary(
            run_id=run_id,
            start_time=datetime.now().isoformat(),
            status=RunStatus.RUNNING,
        )
        self._runs[run_id] = summary
        self._current_run = run_id
        
        # Build pytest command
        cmd = ["pytest", "-v", "--tb=short"]
        
        # Add any additional arguments
        if pytest_args:
            cmd.extend(pytest_args)
        
        # Add test nodeids
        if test_nodeids:
            cmd.extend(test_nodeids)
        
        # Start the pytest subprocess
        # For now, we'll run it synchronously in the background
        # In a real implementation, we'd stream output via a custom pytest plugin
        asyncio.create_task(self._run_pytest(run_id, cmd))
        
        return run_id
    
    async def _run_pytest(self, run_id: str, cmd: list[str]) -> None:
        """Run pytest subprocess and update run status.
        
        Args:
            run_id: The run ID.
            cmd: The pytest command to execute.
        """
        events_path = get_events_path(run_id)
        events_file = None
        
        try:
            # Add our custom plugin and run_id to the command
            plugin_args = [
                "-p", "pw_runner.pytest_plugin",
                "--pw-runner-run-id", run_id,
            ]
            full_cmd = cmd + plugin_args
            
            # Open events file for writing
            events_file = open(events_path, "a")
            
            # Run pytest with timeout
            process = await asyncio.create_subprocess_exec(
                *full_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            self._current_process = process
            
            # Read stderr for events and stdout in parallel to avoid blocking
            async def consume_stdout() -> None:
                """Consume stdout to prevent buffer blocking."""
                if process.stdout:
                    async for line in process.stdout:
                        pass  # Discard stdout output
            
            async def process_events() -> None:
                """Process events from stderr."""
                if process.stderr:
                    async for line in process.stderr:
                        line_str = line.decode().strip()
                        
                        # Check for event lines
                        if line_str.startswith("PW_RUNNER_EVENT:"):
                            event_json = line_str[len("PW_RUNNER_EVENT:"):]
                            try:
                                event = json.loads(event_json)
                                
                                # Write event to file
                                if events_file:
                                    events_file.write(json.dumps(event) + "\n")
                                    events_file.flush()
                                
                                # Update summary based on event
                                self._process_event(run_id, event)
                            except json.JSONDecodeError:
                                pass
            
            # Run both tasks in parallel
            await asyncio.gather(
                consume_stdout(),
                process_events(),
            )
            
            # Wait for completion with timeout (default 1 hour)
            try:
                await asyncio.wait_for(process.wait(), timeout=3600)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise RuntimeError("Test run timed out after 1 hour")
            
            # Update run status
            summary = self._runs[run_id]
            summary.end_time = datetime.now().isoformat()
            if summary.start_time:
                start = datetime.fromisoformat(summary.start_time)
                end = datetime.fromisoformat(summary.end_time)
                summary.duration_seconds = (end - start).total_seconds()
            
            if process.returncode == 0:
                summary.status = RunStatus.COMPLETED
            else:
                summary.status = RunStatus.FAILED
            
            # Save summary
            self._save_run_summary(run_id)
            
        except Exception as e:
            # Log and handle errors
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error running pytest for run {run_id}: {e}")
            
            summary = self._runs.get(run_id)
            if summary:
                summary.status = RunStatus.FAILED
                summary.end_time = datetime.now().isoformat()
                self._save_run_summary(run_id)
        finally:
            # Close events file
            if events_file:
                events_file.close()
            
            # Clear current run
            self._current_run = None
            self._current_process = None
    
    def _process_event(self, run_id: str, event: dict[str, Any]) -> None:
        """Process an event and update run summary.
        
        Args:
            run_id: The run ID.
            event: The event data.
        """
        summary = self._runs.get(run_id)
        if not summary:
            return
        
        event_type = event.get("type")
        
        if event_type == "test_result":
            # Update test counts
            outcome = event.get("outcome")
            if outcome == "passed":
                summary.passed += 1
            elif outcome == "failed":
                summary.failed += 1
            elif outcome == "skipped":
                summary.skipped += 1
            
            summary.total_tests = summary.passed + summary.failed + summary.skipped
            
            # Add test result
            test_result = TestResult(
                nodeid=event.get("nodeid", ""),
                outcome=outcome or "unknown",
                duration_seconds=event.get("duration", 0.0),
                artifacts={}
            )
            summary.tests.append(test_result)
        
        elif event_type == "session_finish":
            # Update final counts from session finish event
            summary.passed = event.get("passed", summary.passed)
            summary.failed = event.get("failed", summary.failed)
            summary.skipped = event.get("skipped", summary.skipped)
            summary.total_tests = event.get("total", summary.total_tests)
    
    def get_run_summary(self, run_id: str) -> Optional[RunSummary]:
        """Get the summary for a specific run.
        
        Args:
            run_id: The run ID.
            
        Returns:
            The run summary, or None if not found.
        """
        # Try to load from memory first
        if run_id in self._runs:
            return self._runs[run_id]
        
        # Try to load from disk
        summary_path = get_run_summary_path(run_id)
        if summary_path.exists():
            with open(summary_path) as f:
                data = json.load(f)
                summary = RunSummary(**data)
                self._runs[run_id] = summary
                return summary
        
        return None
    
    def list_runs(self) -> list[RunSummary]:
        """List all available test runs.
        
        Returns:
            List of run summaries, newest first.
        """
        # Find all run directories
        from pw_runner.models import get_artifact_root
        
        artifact_root = get_artifact_root()
        if not artifact_root.exists():
            return []
        
        summaries = []
        for run_dir in artifact_root.iterdir():
            if run_dir.is_dir() and run_dir.name.startswith("run-"):
                run_id = run_dir.name
                summary = self.get_run_summary(run_id)
                if summary:
                    summaries.append(summary)
        
        # Sort by start time, newest first
        summaries.sort(key=lambda s: s.start_time, reverse=True)
        return summaries
    
    def _save_run_summary(self, run_id: str) -> None:
        """Save run summary to disk.
        
        Args:
            run_id: The run ID.
        """
        summary = self._runs.get(run_id)
        if not summary:
            return
        
        summary_path = get_run_summary_path(run_id)
        with open(summary_path, "w") as f:
            json.dump(summary.model_dump(), f, indent=2)
    
    async def cancel_run(self, run_id: str) -> bool:
        """Cancel a running test run.
        
        Args:
            run_id: The run ID to cancel.
            
        Returns:
            True if the run was cancelled, False if it wasn't running.
        """
        if self._current_run != run_id:
            return False
        
        if self._current_process:
            try:
                self._current_process.terminate()
                await asyncio.wait_for(self._current_process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                self._current_process.kill()
                await self._current_process.wait()
        
        # Update status
        summary = self._runs.get(run_id)
        if summary:
            summary.status = RunStatus.CANCELLED
            summary.end_time = datetime.now().isoformat()
            self._save_run_summary(run_id)
        
        self._current_run = None
        self._current_process = None
        return True


# Global run manager instance
_run_manager: Optional[RunManager] = None


def get_run_manager() -> RunManager:
    """Get the global run manager instance."""
    global _run_manager
    if _run_manager is None:
        _run_manager = RunManager()
    return _run_manager
