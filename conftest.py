"""Pytest configuration and shared fixtures.

This file makes the pw_runner fixtures available to all tests.
"""

# Import fixtures to make them available
pytest_plugins = [
    "pw_runner.pytest_plugin",
    "pw_runner.fixtures",
]
