#!/usr/bin/env python3
"""Command line interface for snippets."""

import importlib.resources
import os
import shutil

import typer
import ulid

app = typer.Typer()


SNIPPETS_TOML_CONTENT = """
[project]
dir = "{snippets_dir}"
schema = "snippets-schema.json"
"""


def ensure_git_repo(folder: str) -> None:
    """Ensure the given folder is a git repository."""
    if not os.path.exists(os.path.join(folder, ".git")):
        typer.echo(f"Error: {folder} is not a git repository")
        raise typer.Exit(1)


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
            schema_content = (
                importlib.resources.files("snippets.assets")
                .joinpath("snippets-schema.json")
                .read_text()
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

    # Create scripts directory if it doesn't exist
    if not os.path.exists(scripts_dir):
        os.makedirs(scripts_dir)
        typer.echo(f"Created scripts directory: {scripts_dir}")

    # Copy snippets-validator.py to scripts directory
    validator_path = os.path.join(scripts_dir, "snippets-validator.py")
    if not os.path.exists(validator_path):
        with open(validator_path, "w") as f:
            validator_content = (
                importlib.resources.files("snippets.assets")
                .joinpath("snippets-validator.py")
                .read_text()
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
        # Read existing content and parse as YAML
        import yaml

        with open(precommit_config_path) as f:
            try:
                config = yaml.safe_load(f) or {}
            except yaml.YAMLError:
                typer.echo(
                    "Warning: Invalid YAML in .pre-commit-config.yaml, skipping update"
                )
                return

        # Ensure repos list exists
        if "repos" not in config:
            config["repos"] = []

        # Find or create local repo section
        local_repo = None
        for repo in config["repos"]:
            if repo.get("repo") == "local":
                local_repo = repo
                break

        if local_repo is None:
            local_repo = {"repo": "local", "hooks": []}
            config["repos"].append(local_repo)

        # Ensure hooks list exists in local repo
        if "hooks" not in local_repo:
            local_repo["hooks"] = []

        # Check if snippets-validator hook already exists
        hook_exists = any(
            hook.get("id") == "snippets-validator" for hook in local_repo["hooks"]
        )

        if not hook_exists:
            # Add the snippets validator hook
            snippets_hook = {
                "id": "snippets-validator",
                "name": "snippets-validator",
                "entry": "python scripts/snippets-validator.py",
                "language": "system",
                "files": r"^snippets/.*\.md$",
                "pass_filenames": True,
            }
            local_repo["hooks"].append(snippets_hook)

            # Write updated config back to file
            with open(precommit_config_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)
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
    ensure_git_repo(folder)

    snippets_dir = os.path.join(folder, "snippets")
    create_snippets_toml(folder, snippets_dir)
    create_snippets_schema(folder)
    create_snippets_directory(snippets_dir)
    create_precommit_setup(folder, os.path.join(folder, "scripts"))

    typer.echo("Snippets project initialized successfully")
    typer.echo("Review changes in git repo and commit them before creating snippets")


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


@app.command()  # type: ignore
def clean(
    folder: str = typer.Argument(".", help="Folder to clean up snippets project in")
) -> None:
    """Clean up a snippets project."""
    typer.echo("Cleaning up a snippets project...")

    if not os.path.exists(folder):
        typer.echo(f"Error: Folder '{folder}' does not exist.", err=True)
        raise typer.Exit(1)

    if os.path.exists(os.path.join(folder, "snippets-schema.json")):
        os.remove(os.path.join(folder, "snippets-schema.json"))
        typer.echo("Removed snippets-schema.json file")
    else:
        typer.echo("snippets-schema.json file does not exist")
        raise typer.Exit(1)

    if os.path.exists(os.path.join(folder, "snippets.toml")):
        os.remove(os.path.join(folder, "snippets.toml"))
        typer.echo("Removed snippets.toml file")
    else:
        typer.echo("snippets.toml file does not exist")
        raise typer.Exit(1)

    if os.path.exists(os.path.join(folder, "snippets")):
        shutil.rmtree(os.path.join(folder, "snippets"))
        typer.echo("Removed snippets directory")
    else:
        typer.echo("snippets directory does not exist")
        raise typer.Exit(1)

    if os.path.exists(os.path.join(folder, "scripts", "snippets-validator.py")):
        os.remove(os.path.join(folder, "scripts", "snippets-validator.py"))
        typer.echo("Removed snippets-validator.py file")
    else:
        typer.echo("snippets-validator.py file does not exist")
        raise typer.Exit(1)


@app.command()  # type: ignore
def add(folder: str = typer.Argument(".", help="Folder to add snippet in")) -> None:
    """Add a new snippet."""
    typer.echo("Adding a new snippet...")

    if not os.path.exists(folder):
        typer.echo(f"Error: Folder '{folder}' does not exist.", err=True)
        raise typer.Exit(1)

    # Find git root by walking up the directory tree
    current_path = os.path.abspath(folder)
    git_root = None

    while current_path != os.path.dirname(current_path):  # Stop at filesystem root
        if os.path.exists(os.path.join(current_path, ".git")):
            git_root = current_path
            break
        current_path = os.path.dirname(current_path)

    if git_root is None:
        typer.echo("Error: Not in a git repository.", err=True)
        raise typer.Exit(1)

    if not os.path.exists(os.path.join(git_root, "snippets")):
        typer.echo("Error: snippets directory does not exist in git root.", err=True)
        raise typer.Exit(1)

    # Generate a new ULID for the snippet
    snippet_id = str(ulid.ULID())
    typer.echo(f"Generated snippet ID: {snippet_id}")

    # Create a new snippet file
    snippet_file = os.path.join(git_root, "snippets", f"{snippet_id}.md")
    if os.path.exists(snippet_file):
        typer.echo(f"Error: Snippet file '{snippet_file}' already exists.", err=True)
        raise typer.Exit(1)

    content = ""

    # Check if content is being piped in
    if not os.isatty(0):  # stdin is not a terminal (i.e., piped input)
        import sys

        content = sys.stdin.read().strip()
    else:
        # Open a temporary file in the system's default editor
        import subprocess
        import tempfile

        # Get the default editor from environment variables
        editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "nano"

        # Create a temporary file
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".md", delete=False
        ) as temp_file:
            temp_file_path = temp_file.name

        try:
            subprocess.run([editor, temp_file_path], check=True)
        except subprocess.CalledProcessError as err:
            typer.echo(f"Error: Failed to open editor '{editor}'.", err=True)
            os.unlink(temp_file_path)  # Clean up temp file
            raise typer.Exit(1) from err
        except FileNotFoundError as err:
            typer.echo(f"Error: Editor '{editor}' not found.", err=True)
            os.unlink(temp_file_path)  # Clean up temp file
            raise typer.Exit(1) from err

        # Read the contents of the temporary file
        try:
            with open(temp_file_path) as temp_file:
                content = temp_file.read().strip()
        finally:
            os.unlink(temp_file_path)  # Clean up temp file

    if content:
        # Create snippet file with YAML front matter
        with open(snippet_file, "w") as f:
            f.write("---\n")
            f.write(f"id: {snippet_id}\n")
            f.write("---\n")
            f.write(content)
            f.write("\n")
    else:
        typer.echo("Error: No content provided.", err=True)
        raise typer.Exit(1)

    typer.echo(f"Created snippet file: {snippet_file}")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
