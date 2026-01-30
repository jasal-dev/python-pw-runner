# Trace File Fix Summary

## Problem
Users reported that trace files were not available after test execution, and tests were running suspiciously fast (~0.4 seconds each), suggesting they weren't actually executing.

## Root Cause
The Playwright fixtures in `src/pw_runner/fixtures.py` were failing during test setup:

```python
# Original code (broken):
run_id = request.config.getoption("--pw-runner-run-id", "local-run")
```

The issue was that `pytest.Config.getoption()` returns `None` when an option is not provided, **even when a default value is specified in the second parameter**. This caused a `TypeError` when trying to construct file paths:

```
TypeError: unsupported operand type(s) for /: 'PosixPath' and 'NoneType'
```

Because the fixture setup failed, tests never actually executed the Playwright browser code, resulting in:
- No trace files created
- Unrealistically fast test execution times
- Silent failures (tests appeared to pass but didn't run)

## Solution
Fixed the fixture to properly handle the missing option:

```python
# Fixed code:
run_id = request.config.getoption("--pw-runner-run-id", default=None) or "local-run"
```

This ensures `run_id` is always a valid string:
- If `--pw-runner-run-id` is provided → use that value
- If not provided → use `"local-run"` as the default

## Verification

### Before Fix
```bash
$ pytest user_tests/saucedemo/test_saucedemo.py::test_invalid_login -v
# ERROR at setup - TypeError
# Duration: 0.4s
# No trace files ❌
```

### After Fix
```bash
$ pytest user_tests/saucedemo/test_saucedemo.py::test_invalid_login -v
# Test executes with Playwright
# Duration: 0.6s-0.8s
# Trace file: .pw-runner/runs/local-run/tests/.../trace.zip (95KB) ✅
```

### Trace File Validation
```bash
$ find .pw-runner/runs -name "trace.zip"
.pw-runner/runs/local-run/tests/user_tests_saucedemo_test_saucedemo_py__test_invalid_login/trace.zip

$ ls -lh .pw-runner/runs/local-run/tests/*/trace.zip
-rw-rw-r-- 1 runner runner 95K ... trace.zip

$ tree .pw-runner/runs/local-run -L 3
.pw-runner/runs/local-run
└── tests
    └── user_tests_saucedemo_test_saucedemo_py__test_invalid_login
        └── trace.zip
```

## Additional Fixes

### Registered Custom Marker
Added to `pyproject.toml` to eliminate warnings:
```toml
[tool.pytest.ini_options]
markers = [
    "example: marks tests as example tests (deselect with '-m \"not example\"')",
]
```

### Updated Documentation
Added section in `README.md` explaining how to view traces:
```bash
playwright show-trace .pw-runner/runs/local-run/tests/<test-name>/trace.zip
```

## Impact
- ✅ Trace files now created for all test runs
- ✅ Tests actually execute browser code
- ✅ Realistic test execution times
- ✅ Works with local pytest runs (run_id="local-run")
- ✅ Works with API-triggered runs (custom run_id)
- ✅ All 38 backend unit tests still pass
- ✅ No breaking changes

## Files Modified
1. `src/pw_runner/fixtures.py` - Fixed run_id default handling
2. `pyproject.toml` - Registered example marker
3. `README.md` - Added trace viewing documentation

## Testing
```bash
# Run backend tests
pytest tests/ -v
# Result: 38 passed ✅

# Run example test locally
pytest user_tests/saucedemo/test_saucedemo.py::test_invalid_login -v
# Result: Creates trace file ✅

# View the trace
playwright show-trace .pw-runner/runs/local-run/tests/*/trace.zip
# Result: Opens trace viewer with captured data ✅
```

## Notes
This was a critical bug that prevented the core functionality (trace capture) from working. The fix is minimal and safe, only affecting the default value handling for the run_id parameter.
