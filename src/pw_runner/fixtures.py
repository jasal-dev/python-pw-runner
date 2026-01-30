"""Pytest fixtures for Playwright tracing and artifact capture.

This module provides fixtures that automatically configure Playwright to
capture traces, screenshots, and videos for all tests.
"""

from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright

from pw_runner.models import ensure_test_dirs, get_test_dir, get_trace_path


@pytest.fixture(scope="session")
def playwright() -> Generator[Playwright, None, None]:
    """Provide a Playwright instance for the test session."""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright: Playwright) -> Generator[Browser, None, None]:
    """Provide a browser instance for the test session."""
    browser = playwright.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture
def context(
    browser: Browser,
    request: pytest.FixtureRequest,
) -> Generator[BrowserContext, None, None]:
    """Provide a browser context with tracing enabled.
    
    This fixture automatically:
    - Creates a new browser context for each test
    - Starts tracing at the beginning of the test
    - Saves the trace to the artifact directory at the end
    - Handles cleanup even if the test fails
    """
    # Get run_id from pytest option or use a default
    run_id = request.config.getoption("--pw-runner-run-id", "local-run")
    nodeid = request.node.nodeid
    
    # Create artifact directory for this test
    test_dir = ensure_test_dirs(run_id, nodeid)
    trace_path = get_trace_path(run_id, nodeid)
    
    # Create context with tracing enabled
    context = browser.new_context()
    
    # Start tracing
    context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True,
    )
    
    yield context
    
    # Stop tracing and save
    try:
        context.tracing.stop(path=str(trace_path))
    except Exception as e:
        # Log error and mark test with warning
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to save trace for {nodeid}: {e}")
        pytest.fail(f"Trace capture failed: {e}", pytrace=False)
    finally:
        context.close()


@pytest.fixture
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Provide a new page for each test."""
    page = context.new_page()
    yield page
    page.close()


# Register fixtures as plugins
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom options."""
    # Ensure our fixtures are available
    pass


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command-line options."""
    parser.addoption(
        "--pw-runner-output-dir",
        action="store",
        default=None,
        help="Output directory for test artifacts",
    )
