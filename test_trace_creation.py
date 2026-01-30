#!/usr/bin/env python
"""Test script to verify trace files are created properly."""

import subprocess
import sys
from pathlib import Path


def main():
    """Run a test and verify trace file is created."""
    # Clean up any previous local-run
    local_run_dir = Path(".pw-runner/runs/local-run")
    if local_run_dir.exists():
        import shutil
        shutil.rmtree(local_run_dir)
    
    # Run a single test
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "user_tests/saucedemo/test_saucedemo.py::test_invalid_login",
            "-v",
            "--tb=short",
        ],
        capture_output=True,
        text=True,
    )
    
    print("Test output:")
    print(result.stdout)
    print(result.stderr)
    
    # Check if trace file was created
    trace_files = list(Path(".pw-runner/runs/local-run/tests").rglob("trace.zip"))
    
    if not trace_files:
        print("\n❌ FAILED: No trace files found!")
        return 1
    
    trace_file = trace_files[0]
    size_kb = trace_file.stat().st_size / 1024
    
    print(f"\n✅ SUCCESS: Trace file created!")
    print(f"   Location: {trace_file}")
    print(f"   Size: {size_kb:.1f} KB")
    
    if size_kb < 10:
        print(f"\n⚠️  WARNING: Trace file seems small ({size_kb:.1f} KB)")
        print("   This might indicate the test didn't execute properly")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
