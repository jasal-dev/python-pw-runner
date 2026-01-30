"""FastAPI application for the Python Playwright Test Runner backend."""

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pw_runner.discovery import DiscoveredTest, discover_tests, group_tests_by_file
from pw_runner.models import get_artifact_root
from pw_runner.runner import RunSummary, get_run_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifespan events."""
    # Startup: ensure artifact directory exists
    artifact_root = get_artifact_root()
    artifact_root.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Shutdown: cleanup if needed
    # (For MVP, we don't need special cleanup)


# Create FastAPI application
app = FastAPI(
    title="Python Playwright Test Runner",
    description="A graphical test runner for Python + pytest + Playwright",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for artifacts
# We'll serve artifacts from the .pw-runner/runs directory
try:
    artifact_root = get_artifact_root()
    artifact_root.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/artifacts",
        StaticFiles(directory=str(artifact_root)),
        name="artifacts"
    )
except Exception as e:
    # Log error during artifact directory setup
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to mount artifacts directory: {e}")


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint - API status."""
    return {
        "name": "Python Playwright Test Runner API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Request/Response models
class StartRunRequest(BaseModel):
    """Request to start a new test run."""
    test_nodeids: list[str]
    pytest_args: Optional[list[str]] = None


class StartRunResponse(BaseModel):
    """Response from starting a test run."""
    run_id: str
    status: str


# Run management endpoints
@app.post("/api/runs", response_model=StartRunResponse)
async def start_run(request: StartRunRequest) -> StartRunResponse:
    """Start a new test run.
    
    Args:
        request: The run request containing test nodeids and options.
        
    Returns:
        The run ID and status.
        
    Raises:
        HTTPException: If a run is already in progress.
    """
    manager = get_run_manager()
    
    try:
        run_id = await manager.start_run(
            test_nodeids=request.test_nodeids,
            pytest_args=request.pytest_args,
        )
        return StartRunResponse(run_id=run_id, status="running")
    except RuntimeError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.get("/api/runs/{run_id}", response_model=RunSummary)
async def get_run(run_id: str) -> RunSummary:
    """Get the status and summary of a specific test run.
    
    Args:
        run_id: The run ID.
        
    Returns:
        The run summary.
        
    Raises:
        HTTPException: If the run is not found.
    """
    manager = get_run_manager()
    summary = manager.get_run_summary(run_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return summary


@app.get("/api/runs", response_model=list[RunSummary])
async def list_runs() -> list[RunSummary]:
    """List all available test runs.
    
    Returns:
        List of run summaries, newest first.
    """
    manager = get_run_manager()
    return manager.list_runs()


@app.delete("/api/runs/{run_id}")
async def cancel_run(run_id: str) -> dict[str, str]:
    """Cancel a running test run.
    
    Args:
        run_id: The run ID to cancel.
        
    Returns:
        Status message.
        
    Raises:
        HTTPException: If the run is not currently running.
    """
    manager = get_run_manager()
    cancelled = await manager.cancel_run(run_id)
    
    if not cancelled:
        raise HTTPException(
            status_code=400,
            detail="Run is not currently running or does not exist"
        )
    
    return {"status": "cancelled", "run_id": run_id}


# Test discovery endpoints
class TestInfoResponse(BaseModel):
    """Response model for test information."""
    nodeid: str
    file_path: str
    class_name: Optional[str]
    function_name: str
    markers: list[str]


class TestDiscoveryResponse(BaseModel):
    """Response model for test discovery."""
    tests: list[TestInfoResponse]
    total: int
    grouped_by_file: dict[str, list[TestInfoResponse]]


@app.get("/api/tests", response_model=TestDiscoveryResponse)
async def discover_tests_endpoint(
    path: Optional[str] = Query(None, description="Path to limit test discovery"),
    keyword: Optional[str] = Query(None, description="Keyword filter (-k)"),
    marker: Optional[str] = Query(None, description="Marker filter (-m)"),
) -> TestDiscoveryResponse:
    """Discover available tests using pytest's collection mechanism.
    
    Args:
        path: Optional path to limit test discovery.
        keyword: Optional keyword filter.
        marker: Optional marker filter.
        
    Returns:
        Discovered tests and metadata.
        
    Raises:
        HTTPException: If test discovery fails.
    """
    try:
        tests = discover_tests(path=path, keyword=keyword, marker=marker)
        
        # Convert to response models
        test_responses = [
            TestInfoResponse(
                nodeid=t.nodeid,
                file_path=t.file_path,
                class_name=t.class_name,
                function_name=t.function_name,
                markers=t.markers,
            )
            for t in tests
        ]
        
        # Group by file
        grouped = group_tests_by_file(tests)
        grouped_responses = {
            file_path: [
                TestInfoResponse(
                    nodeid=t.nodeid,
                    file_path=t.file_path,
                    class_name=t.class_name,
                    function_name=t.function_name,
                    markers=t.markers,
                )
                for t in file_tests
            ]
            for file_path, file_tests in grouped.items()
        }
        
        return TestDiscoveryResponse(
            tests=test_responses,
            total=len(test_responses),
            grouped_by_file=grouped_responses,
        )
    
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
