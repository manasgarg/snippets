# Python Project

A Python project with comprehensive lint and test automation.

## 🚀 Features

- **Code Quality**: Automated linting with Ruff, Black, isort, and MyPy
- **Testing**: Pytest with coverage reporting
- **CI/CD**: GitHub Actions workflow for continuous integration
- **Pre-commit Hooks**: Automated code quality checks before commits
- **Modern Tooling**: Built with uv for fast dependency management

## 📋 Prerequisites

- Python 3.11+
- uv (Python package manager)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd python-project
   ```

2. **Install dependencies:**
   ```bash
   # Install production dependencies
   uv sync
   
   # Install development dependencies
   uv sync --group dev
   ```

3. **Install pre-commit hooks (optional):**
   ```bash
   uv add --dev pre-commit
   pre-commit install
   ```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_main.py

# Run tests with markers
uv run pytest -m "not slow"
```

### Test Coverage
```bash
# Generate HTML coverage report
uv run pytest --cov=. --cov-report=html

# View coverage in terminal
uv run pytest --cov=. --cov-report=term-missing
```

## 🔍 Linting & Formatting

### Code Formatting
```bash
# Format code with Black
uv run black .

# Sort imports with isort
uv run isort .

# Format and sort in one command
make format
```

### Code Quality Checks
```bash
# Run Ruff linter
uv run ruff check .

# Run MyPy type checker
uv run mypy .

# Run all linting tools
make lint
```

## 🚀 Automation with Make

The project includes a Makefile for common tasks:

```bash
# Show all available commands
make help

# Install dependencies
make install-dev

# Run all checks (format, lint, check, test)
make all

# Clean up generated files
make clean
```

## 🔧 Configuration

### Tools Configuration

- **Black**: Code formatting (88 character line length)
- **isort**: Import sorting (compatible with Black)
- **Ruff**: Fast Python linter with auto-fix
- **MyPy**: Static type checking
- **Pytest**: Testing framework with coverage

### Pre-commit Hooks

Automated checks run before each commit:
- Code formatting (Black)
- Import sorting (isort)
- Linting (Ruff)
- Type checking (MyPy)
- Basic file checks

## 📊 Continuous Integration

GitHub Actions workflow runs on:
- Push to main/master/develop branches
- Pull requests to main/master/develop branches

**CI Pipeline:**
1. Lint with Ruff
2. Check formatting with Black
3. Check import sorting with isort
4. Type check with MyPy
5. Run tests with pytest
6. Generate coverage reports

## 🏗️ Project Structure

```
python-project/
├── .github/workflows/    # CI/CD workflows
├── tests/                # Test files
│   ├── __init__.py
│   └── test_main.py
├── .gitignore           # Git ignore patterns
├── .pre-commit-config.yaml  # Pre-commit hooks
├── Makefile             # Development automation
├── main.py              # Main application code
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

## 🧹 Development Workflow

1. **Make changes** to your code
2. **Format code**: `make format`
3. **Check quality**: `make lint`
4. **Run tests**: `make test`
5. **Commit changes**: Git will run pre-commit hooks automatically

## 📝 Adding New Dependencies

```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Add with specific version
uv add "package-name>=1.0.0"
```

## 🐛 Troubleshooting

### Common Issues

1. **Pre-commit hooks failing**: Run `make format` and `make lint` to fix issues
2. **Type checking errors**: Add type hints or use `# type: ignore` comments
3. **Test failures**: Check test output and fix failing assertions

### Getting Help

- Check the tool documentation:
  - [Ruff](https://docs.astral.sh/ruff/)
  - [Black](https://black.readthedocs.io/)
  - [MyPy](https://mypy.readthedocs.io/)
  - [Pytest](https://docs.pytest.org/)

## 📄 License

This project is licensed under the MIT License.
