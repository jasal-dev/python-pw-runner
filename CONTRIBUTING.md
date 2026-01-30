# Contributing to Python Playwright Test Runner

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/python-pw-runner.git
   cd python-pw-runner
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   playwright install chromium
   ```

4. **Verify the installation**
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following the project style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests**
   ```bash
   # Run all tests
   pytest tests/ -v
   
   # Run specific test file
   pytest tests/test_api.py -v
   ```

4. **Check code quality**
   ```bash
   # Format code
   black src/ tests/
   
   # Check linting
   ruff check src/ tests/
   
   # Type checking
   mypy src/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style

- **Python version**: Target Python 3.8+ for compatibility
- **Formatting**: Use `black` with default settings (100 character line length)
- **Linting**: Follow `ruff` recommendations
- **Type hints**: Add type annotations to all functions
- **Docstrings**: Use Google-style docstrings for modules, classes, and functions

### Example

```python
def sanitize_nodeid(nodeid: str) -> str:
    """Sanitize a pytest nodeid to create a filesystem-safe directory name.
    
    Args:
        nodeid: The pytest test nodeid.
        
    Returns:
        A filesystem-safe string suitable for use as a directory name.
    """
    # Implementation
    pass
```

## Testing

- Write tests for all new features
- Maintain or improve test coverage
- Use pytest fixtures appropriately
- Tests should be isolated and repeatable

### Test Structure

```python
class TestFeature:
    """Tests for feature X."""
    
    def test_specific_behavior(self) -> None:
        """Test that feature X does Y."""
        # Arrange
        input_data = "test"
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_output
```

## Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update API documentation if endpoints change

## Pull Request Process

1. **Ensure all tests pass**
2. **Update documentation**
3. **Add entry to CHANGELOG.md** (if applicable)
4. **Request review from maintainers**
5. **Address review feedback**
6. **Squash commits if requested**

### Pull Request Template

```markdown
## Description
Brief description of the changes

## Related Issue
Fixes #123

## Changes Made
- Added feature X
- Fixed bug in Y
- Updated documentation

## Testing
- [ ] All existing tests pass
- [ ] Added tests for new functionality
- [ ] Manually tested the changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## Issue Reporting

### Bug Reports

Include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages or logs

### Feature Requests

Include:
- Problem you're trying to solve
- Proposed solution
- Alternative solutions considered
- Additional context

## Project Structure

```
python-pw-runner/
├── src/pw_runner/          # Main package
│   ├── api.py             # FastAPI application
│   ├── runner.py          # Test run management
│   ├── discovery.py       # Test discovery
│   ├── models.py          # Data models
│   ├── pytest_plugin.py   # Event streaming
│   └── fixtures.py        # Playwright fixtures
├── tests/                 # Unit tests
│   ├── test_api.py
│   ├── test_runner.py
│   ├── test_discovery.py
│   └── test_models.py
├── examples/              # Example test suites
├── docs/                  # Documentation
└── .github/workflows/     # CI configuration
```

## Getting Help

- **Documentation**: Check the README.md and docs/ directory
- **Issues**: Search existing issues before creating new ones
- **Discussions**: Use GitHub Discussions for questions

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (to be determined).

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what's best for the community
- Show empathy towards other community members
