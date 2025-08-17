#!/usr/bin/env python3
"""Command line interface for snippets."""

import importlib.resources
import os

import typer

app = typer.Typer()


SNIPPETS_TOML_CONTENT = """
[project]
dir = "{snippets_dir}"
schema = "snippets-schema.json"
"""


def create_snippets_toml(folder: str, snippets_dir: str) -> None:
    """Create a snippets.toml file in the given folder."""
    snippets_toml_path = os.path.join(folder, "snippets.toml")
    if not os.path.exists(snippets_toml_path):
        with open(snippets_toml_path, "w") as f:
            f.write(SNIPPETS_TOML_CONTENT.format(snippets_dir=snippets_dir))
            typer.echo(f"Created snippets.toml file: {snippets_toml_path}")


def create_snippets_schema(folder: str) -> None:
    """Create a snippets schema file in the given folder."""
    # Create snippets-schema.json file
    snippets_schema_path = os.path.join(folder, "snippets-schema.json")
    if not os.path.exists(snippets_schema_path):
        with open(snippets_schema_path, "w") as f:
            schema_content = importlib.resources.read_text(
                "snippets.assets", "snippets-schema.json"
            )
            f.write(schema_content)
            typer.echo(f"Created snippets-schema.json file: {snippets_schema_path}")
    else:
        typer.echo(f"snippets-schema.json file already exists: {snippets_schema_path}")
        raise typer.Exit(1)


def create_snippets_directory(snippets_dir: str) -> None:
    """Create a snippets directory in the given folder."""
    if not os.path.exists(snippets_dir):
        os.makedirs(snippets_dir)
        typer.echo(f"Created snippets directory: {snippets_dir}")
    else:
        typer.echo(f"Snippets directory already exists: {snippets_dir}")


def create_precommit_setup(folder: str, scripts_dir: str) -> None:
    """Create pre-commit setup with snippets validation."""

    # Copy snippets-validator.py to scripts directory
    validator_path = os.path.join(scripts_dir, "snippets-validator.py")
    if not os.path.exists(validator_path):
        with open(validator_path, "w") as f:
            validator_content = importlib.resources.read_text(
                "snippets.assets", "snippets-validator.py"
            )
            f.write(validator_content)
        # Make the script executable
        os.chmod(validator_path, 0o755)
        typer.echo(f"Created snippets-validator.py script: {validator_path}")

    # Create or update .pre-commit-config.yaml
    precommit_config_path = os.path.join(folder, ".pre-commit-config.yaml")

    # Pre-commit hook configuration for snippets validator
    snippets_hook_config = """
  - repo: local
    hooks:
      - id: snippets-validator
        name: snippets-validator
        entry: python scripts/snippets-validator.py
        language: system
        files: ^snippets/.*\\.md$
        pass_filenames: true"""

    if os.path.exists(precommit_config_path):
        # Read existing content and check if snippets validator is already present
        with open(precommit_config_path) as f:
            existing_content = f.read()

        if "snippets-validator" not in existing_content:
            # Append the snippets validator hook
            with open(precommit_config_path, "a") as f:
                f.write(snippets_hook_config)
            typer.echo("Updated .pre-commit-config.yaml with snippets validator hook")
        else:
            typer.echo(
                ".pre-commit-config.yaml already contains snippets validator hook"
            )
    else:
        # Create new .pre-commit-config.yaml with basic setup
        precommit_content = f"""repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer{snippets_hook_config}
"""
        with open(precommit_config_path, "w") as f:
            f.write(precommit_content)
        typer.echo(f"Created .pre-commit-config.yaml file: {precommit_config_path}")

    # Check if pre-commit is installed
    try:
        import subprocess

        result = subprocess.run(
            ["pre-commit", "--version"], capture_output=True, text=True
        )
        if result.returncode != 0:
            raise FileNotFoundError
    except (FileNotFoundError, subprocess.SubprocessError):
        typer.echo(
            "Warning: pre-commit is not installed. Install it with: pip install pre-commit"
        )
        typer.echo("After installation, run: pre-commit install")


def init_snippets(folder: str) -> None:
    """Initialize a snippets project in the given folder.

    Args:
        folder: The folder to initialize the snippets project in.
    """
    snippets_dir = os.path.join(folder, "snippets")
    create_snippets_toml(folder, snippets_dir)
    create_snippets_schema(folder)
    create_snippets_directory(snippets_dir)
    create_precommit_setup(folder, os.path.join(folder, "scripts"))


@app.callback()  # type: ignore
def callback() -> None:
    """Snippets command line utility."""
    pass


@app.command()  # type: ignore
def init(
    folder: str = typer.Argument(".", help="Folder to initialize snippets project in")
) -> None:
    """Initialize a new snippets project."""
    typer.echo(f"Initializing a new snippets project in {folder}...")

    if not os.path.exists(folder):
        typer.echo(f"Error: Folder '{folder}' does not exist.", err=True)
        raise typer.Exit(1)

    init_snippets(folder)


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
