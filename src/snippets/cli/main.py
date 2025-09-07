#!/usr/bin/env python3
"""Command line interface for snippets."""

import typer

app = typer.Typer()


@app.callback()
def callback() -> None:
    """Snippets command line utility."""
    pass


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
