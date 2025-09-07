import importlib.resources
import os

import typer

from snippets.cli.main import app

SNIPPETS_TOML_CONTENT = """
[project]
dir = "{snippets_dir}"
schema = "snippets-schema.json"
"""


def ensure_git_repo(repo: str) -> None:
    """Ensure the given repo is a git repository."""
    if not os.path.exists(os.path.join(repo, ".git")):
        typer.echo(f"Error: {repo} is not a git repository")
        raise typer.Exit(1)


def create_snippets_toml(repo: str, snippets_dir: str) -> None:
    """Create a snippets.toml file in the given repo."""
    snippets_toml_path = os.path.join(repo, "snippets.toml")
    if not os.path.exists(snippets_toml_path):
        with open(snippets_toml_path, "w") as f:
            f.write(SNIPPETS_TOML_CONTENT.format(snippets_dir=snippets_dir))
            typer.echo(f"Created snippets.toml file: {snippets_toml_path}")


def create_snippets_schema(repo: str) -> None:
    """Create a snippets schema file in the given repo."""
    # Create snippets-schema.json file
    snippets_schema_path = os.path.join(repo, "snippets-schema.json")
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


def create_precommit_setup(repo: str, scripts_dir: str) -> None:
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
    precommit_config_path = os.path.join(repo, ".pre-commit-config.yaml")

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
        local_repo_config = None
        for repo_config in config["repos"]:
            if repo_config.get("repo") == "local":
                local_repo_config = repo_config
                break

        if local_repo_config is None:
            local_repo_config = {"repo": "local", "hooks": []}
            config["repos"].append(local_repo_config)

        # Ensure hooks list exists in local repo
        if "hooks" not in local_repo_config:
            local_repo_config["hooks"] = []

        # Check if snippets-validator hook already exists
        hook_exists = any(
            hook.get("id") == "snippets-validator"
            for hook in local_repo_config["hooks"]
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
            local_repo_config["hooks"].append(snippets_hook)

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


def init_snippets(repo: str) -> None:
    """Initialize a snippets project in the given folder.

    Args:
        folder: The folder to initialize the snippets project in.
    """
    ensure_git_repo(repo)

    snippets_dir = os.path.join(repo, "snippets")
    create_snippets_toml(repo, snippets_dir)
    create_snippets_schema(repo)
    create_snippets_directory(snippets_dir)
    create_precommit_setup(repo, os.path.join(repo, "scripts"))

    typer.echo("Snippets project initialized successfully")
    typer.echo("Review changes in git repo and commit them before creating snippets")


@app.command()
def init(
    repo: str = typer.Argument(
        ".", help="Git repository to initialize snippets project in"
    )
) -> None:
    """Initialize a new snippets project."""
    typer.echo(f"Initializing a new snippets project in {repo}...")

    if not os.path.exists(repo):
        typer.echo(f"Error: Folder '{repo}' does not exist.", err=True)
        raise typer.Exit(1)

    init_snippets(repo)
