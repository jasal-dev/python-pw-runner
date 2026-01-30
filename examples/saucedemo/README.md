# Example Playwright Tests for Saucedemo.com

This directory contains example Playwright tests for the [Sauce Labs demo e-commerce site](https://www.saucedemo.com/).

## Purpose

These tests serve as:
1. **Reference examples** - Demonstrate Playwright best practices with pytest
2. **Demo tests** - Showcase the Python Playwright Test Runner's capabilities
3. **Test data** - Provide real tests for exercising the test runner UI

## Test Coverage

The test suite covers the following functionality:

### Authentication (`test_valid_login`, `test_invalid_login`)
- Valid login with correct credentials
- Invalid login with incorrect credentials

### Inventory (`TestInventory`)
- Viewing the product inventory page
- Adding products to the shopping cart

### Cart (`TestCart`)
- Viewing items in the shopping cart
- Removing items from the cart

### Checkout (`TestCheckout`)
- Entering checkout information
- Completing a purchase end-to-end

## Running the Tests

### Prerequisites

1. Install dependencies:
   ```bash
   pip install -e .
   playwright install chromium
   ```

2. The tests use the following credentials for the demo site:
   - **Username:** `standard_user`
   - **Password:** `secret_sauce`

### Running Tests Directly

Run all example tests:
```bash
pytest examples/saucedemo/ -v
```

Run tests with the example marker:
```bash
pytest -m example -v
```

Run a specific test:
```bash
pytest examples/saucedemo/test_saucedemo.py::test_valid_login -v
```

### Running with Trace Capture

To capture Playwright traces for debugging:
```bash
pytest examples/saucedemo/ -v --pw-runner-run-id=local-test
```

Traces will be saved to `.pw-runner/runs/local-test/tests/`.

### Running with the Test Runner UI

1. Start the test runner backend:
   ```bash
   pw-runner
   ```

2. The API will be available at `http://localhost:8000`

3. Use the `/api/tests` endpoint to discover these tests

4. Use the `/api/runs` endpoint to execute tests and view results

## Test Structure

All tests follow Playwright best practices:

- **Page fixture** - Each test receives a `page` fixture with automatic tracing
- **Explicit waits** - Tests use Playwright's auto-waiting for elements
- **Selectors** - Tests use CSS selectors and data-test attributes
- **Assertions** - Tests verify expected outcomes using pytest assertions

## Markers

Tests are marked with `@pytest.mark.example` to allow filtering:

```python
@pytest.mark.example
def test_valid_login(page):
    # Test implementation
    pass
```

Filter tests by marker:
```bash
pytest -m example
```

## Expected Behavior

All tests should pass when run against https://www.saucedemo.com/. The site is a stable demo application maintained by Sauce Labs for testing purposes.

## Trace Files

When tests run with the test runner, trace files are automatically captured and saved to:

```
.pw-runner/runs/<run-id>/tests/<test-nodeid>/trace.zip
```

View traces using:
```bash
playwright show-trace .pw-runner/runs/<run-id>/tests/<test-nodeid>/trace.zip
```

## Troubleshooting

**Tests failing with timeout errors:**
- Check your internet connection
- The saucedemo.com site may be temporarily unavailable
- Increase timeout values if needed

**Traces not being captured:**
- Ensure you're using the `page` fixture from `pw_runner.fixtures`
- Check that the `--pw-runner-run-id` option is provided

**Browser not launching:**
- Run `playwright install` to install browser binaries
- Check that chromium is installed: `playwright install chromium`
