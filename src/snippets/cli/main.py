#!/usr/bin/env python3
"""Command line interface for snippets."""


import typer

app = typer.Typer()


@app.callback()  # type: ignore
def callback() -> None:
    """Snippets command line utility."""
    pass


@app.command()  # type: ignore
def hello() -> None:
    """Print 'world'."""
    typer.echo("world")


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
