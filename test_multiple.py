"""Test to reproduce the multiple test issue."""

import pytest
import time


@pytest.mark.example
def test_first(page):
    """First test - should work."""
    # Just navigate to a simple page
    page.goto("data:text/html,<h1>Test 1</h1>")
    time.sleep(0.1)  # Simulate some work
    assert page.title() == ""


@pytest.mark.example
def test_second(page):
    """Second test - should also work."""
    # Just navigate to a simple page
    page.goto("data:text/html,<h1>Test 2</h1>")
    time.sleep(0.1)  # Simulate some work
    assert page.title() == ""


@pytest.mark.example
def test_third(page):
    """Third test - should also work."""
    # Just navigate to a simple page
    page.goto("data:text/html,<h1>Test 3</h1>")
    time.sleep(0.1)  # Simulate some work
    assert page.title() == ""
