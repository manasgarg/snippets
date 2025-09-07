import os
from datetime import datetime

import typer
import ulid
import yaml

from snippets.cli.main import app
from snippets.sdk.decorators.sluggen import SlugGenerator


def find_git_root(repo: str) -> str:
    """Find the git root directory by walking up the directory tree.

    Args:
        repo: Starting directory path to search from.

    Returns:
        Path to the git root directory.

    Raises:
        typer.Exit: If no git repository is found.
    """
    current_path = os.path.abspath(repo)

    while current_path != os.path.dirname(current_path):  # Stop at filesystem root
        if os.path.exists(os.path.join(current_path, ".git")):
            return current_path
        current_path = os.path.dirname(current_path)

    typer.echo("Error: Not in a git repository.", err=True)
    raise typer.Exit(1)


def validate_snippets_setup(git_root: str) -> None:
    """Validate that the snippets directory exists in the git root.

    Args:
        git_root: Path to the git root directory.

    Raises:
        typer.Exit: If snippets directory doesn't exist.
    """
    if not os.path.exists(os.path.join(git_root, "snippets")):
        typer.echo("Error: snippets directory does not exist in git root.", err=True)
        raise typer.Exit(1)


def get_snippet_content_from_editor(metadata: dict) -> tuple[str, dict]:
    """Get snippet content by opening the system's default editor.

    Returns:
        Tuple of (content, metadata) where content is the snippet text
        and metadata is any YAML front matter.

    Raises:
        typer.Exit: If editor fails to open or read.
    """
    import subprocess
    import tempfile

    # Get the default editor from environment variables
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "vim"

    # Create a temporary file
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".md", delete=False
    ) as temp_file:
        # if metadata is not empty, write it to the temporary file
        if metadata:
            temp_file.write("---\n")
            for key, value in metadata.items():
                temp_file.write(f"{key}: {value}\n")
            temp_file.write("---\n\n")

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
            metadata = {}

            if content.startswith("---"):
                parts = content.split("---")
                if len(parts) >= 3:
                    metadata_str = parts[1].strip()
                    metadata = yaml.safe_load(metadata_str) or {}
                    content = parts[2].strip()

    finally:
        os.unlink(temp_file_path)  # Clean up temp file

    return content, metadata


def get_snippet_content(title: str, text: str) -> tuple[str, dict]:
    """Get snippet content from text argument or editor input.

    Args:
        text: Text content provided as argument.

    Returns:
        Tuple of (content, metadata) where content is the snippet text
        and metadata is any YAML front matter.
    """
    content = text
    metadata = {}
    if title:
        metadata["title"] = title

    if not content:
        # Check if content is being piped in
        if not os.isatty(0):  # stdin is not a terminal (i.e., piped input)
            import sys

            content = sys.stdin.read().strip()
        else:
            # Open editor for interactive input
            content, metadata = get_snippet_content_from_editor(metadata)

    return content, metadata


def create_snippet_file(
    git_root: str, snippet_id: str, title: str, slug: str, content: str
) -> str:
    """Create the snippet file with proper formatting.

    Args:
        git_root: Path to the git root directory.
        snippet_id: Unique identifier for the snippet.
        title: Title of the snippet.
        slug: URL-friendly slug for the snippet.
        content: Text content of the snippet.

    Returns:
        Path to the created snippet file.

    Raises:
        typer.Exit: If snippet file already exists.
    """
    snippet_file_name = f"{slug}.md" if slug else f"{snippet_id}.md"
    snippet_file = os.path.join(git_root, "snippets", snippet_file_name)

    if os.path.exists(snippet_file):
        typer.echo(f"Error: Snippet file '{snippet_file}' already exists.", err=True)
        raise typer.Exit(1)

    # Create snippet file with YAML front matter
    with open(snippet_file, "w") as f:
        f.write("---\n")
        f.write(f"id: {snippet_id}\n")
        f.write(f"title: {title}\n")
        f.write(f"slug: {slug}\n")
        f.write(f"created_at: {datetime.now().isoformat()}\n")
        f.write(f"updated_at: {datetime.now().isoformat()}\n")
        f.write("---\n\n")
        f.write(content)
        f.write("\n")

    return snippet_file


@app.command()
def add(
    repo: str = typer.Option(".", help="Git repository to add snippet in"),
    title: str = typer.Option("", help="Title of the snippet"),
    text: str = typer.Argument("", help="Text content of the snippet"),
) -> None:
    """Add a new snippet."""
    typer.echo("Adding a new snippet...")

    if not os.path.exists(repo):
        typer.echo(f"Error: Folder '{repo}' does not exist.", err=True)
        raise typer.Exit(1)

    # Find git root and validate setup
    git_root = find_git_root(repo)
    validate_snippets_setup(git_root)

    # Generate a new ULID for the snippet
    snippet_id = str(ulid.ULID())
    typer.echo(f"Generated snippet ID: {snippet_id}")

    # Get snippet content
    content, metadata = get_snippet_content(title, text)
    title = metadata.get("title", "")
    slug = metadata.get("slug", "")

    if not content:
        typer.echo("Error: No content provided.", err=True)
        raise typer.Exit(1)

    if title and not slug:
        # Generate slug from title
        slug = SlugGenerator().generate_slug(title) if title else ""

    # Create the snippet file
    snippet_file = create_snippet_file(git_root, snippet_id, title, slug, content)
    typer.echo(f"Created snippet file: {snippet_file}")
