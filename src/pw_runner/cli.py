"""Command-line interface for the Python Playwright Test Runner."""

import argparse
import os
import sys

import uvicorn


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Python Playwright Test Runner - A graphical test runner for pytest + Playwright"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind the server to (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    parser.add_argument(
        "--test-path",
        default="user_tests",
        help="Default path for discovering user tests (default: user_tests)",
    )
    
    args = parser.parse_args()
    
    # Set the default test path as an environment variable for the API to use
    os.environ["PW_RUNNER_TEST_PATH"] = args.test_path
    
    print(f"Starting Python Playwright Test Runner on http://{args.host}:{args.port}")
    print(f"Default test path: {args.test_path}")
    print("Press Ctrl+C to stop the server")
    
    uvicorn.run(
        "pw_runner.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
