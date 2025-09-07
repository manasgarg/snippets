.PHONY: help install install-dev test test-cov lint format check clean

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run all linting tools"
	@echo "  format       - Format code with black and isort"
	@echo "  check        - Run type checking with mypy"
	@echo "  clean        - Clean up generated files"
	@echo "  all          - Run format, lint, check, and test"

# Install production dependencies
install:
	uv sync
	uv pip install -e .

# Install development dependencies
install-dev:
	uv sync --group dev

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=. --cov-report=html --cov-report=term-missing

# Run all linting tools
lint:
	@echo "Running ruff..."
	uv run ruff check .
	@echo "Running mypy..."
	uv run mypy .
	@echo "All linting passed! ✨"

# Format code
format:
	@echo "Formatting with black..."
	uv run black .
	@echo "Sorting imports with isort..."
	uv run isort .
	@echo "Code formatting complete! ✨"

# Type checking
check:
	uv run mypy .

# Clean up generated files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf build/ dist/ .tox/ .ruff_cache/

# Run all checks
all: format lint test
	@echo "All checks passed! 🎉"
