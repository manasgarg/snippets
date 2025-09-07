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
