# User Tests

This directory contains your Playwright tests that will be displayed in the UI.

## Purpose

Place your test files here to have them automatically discovered and displayed in the Python Playwright Test Runner UI. The tests in this directory are what end users will see and run through the graphical interface.

## Structure

You can organize your tests in subdirectories as needed:

```
user_tests/
├── saucedemo/           # Example: SauceDemo tests
│   ├── test_saucedemo.py
│   └── README.md
├── my_app/              # Your application tests
│   ├── test_login.py
│   └── test_checkout.py
└── README.md            # This file
```

## Getting Started

1. Create a new directory for your test suite (e.g., `my_app/`)
2. Add your test files following pytest conventions (`test_*.py`)
3. The tests will automatically appear in the UI when you start the server

## Example Test

See `saucedemo/test_saucedemo.py` for a complete example of Playwright tests.

```python
import pytest

def test_example(page):
    """Example test that will appear in the UI."""
    page.goto("https://example.com")
    assert page.title() == "Example Domain"
```

## Running Tests

Tests in this directory can be run:

1. **Through the UI**: Start `pw-runner` and select tests from the web interface
2. **Command line**: `pytest user_tests/` to run all user tests
3. **Specific tests**: `pytest user_tests/my_app/test_login.py::test_valid_login`

## Notes

- Tests in the `tests/` directory (backend unit tests) are NOT shown in the UI by default
- This separation keeps your user-facing tests clean and focused
- You can customize the test discovery path using the `--test-path` CLI argument
