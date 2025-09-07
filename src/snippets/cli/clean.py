import os
import shutil

import typer

from snippets.cli.main import app


@app.command()
def clean(
    repo: str = typer.Argument(
        ".", help="Git repository to clean up snippets project in"
    )
) -> None:
    """Clean up a snippets project."""
    typer.echo("Cleaning up a snippets project...")

    if not os.path.exists(repo):
        typer.echo(f"Error: Folder '{repo}' does not exist.", err=True)
        raise typer.Exit(1)

    if os.path.exists(os.path.join(repo, "snippets-schema.json")):
        os.remove(os.path.join(repo, "snippets-schema.json"))
        typer.echo("Removed snippets-schema.json file")
    else:
        typer.echo("snippets-schema.json file does not exist")
        raise typer.Exit(1)

    if os.path.exists(os.path.join(repo, "snippets.toml")):
        os.remove(os.path.join(repo, "snippets.toml"))
        typer.echo("Removed snippets.toml file")
    else:
        typer.echo("snippets.toml file does not exist")
        raise typer.Exit(1)

    if os.path.exists(os.path.join(repo, "snippets")):
        shutil.rmtree(os.path.join(repo, "snippets"))
        typer.echo("Removed snippets directory")
    else:
        typer.echo("snippets directory does not exist")
        raise typer.Exit(1)

    if os.path.exists(os.path.join(repo, "scripts", "snippets-validator.py")):
        os.remove(os.path.join(repo, "scripts", "snippets-validator.py"))
        typer.echo("Removed snippets-validator.py file")
    else:
        typer.echo("snippets-validator.py file does not exist")
        raise typer.Exit(1)
