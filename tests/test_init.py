import os
import tempfile

import pytest
import typer

from snippets.cli.init import init


def test_init_nonexisting_directory() -> None:
    """Test that init command fails when directory doesn't exist."""
    with tempfile.TemporaryDirectory() as temp_dir:
        nonexistent_dir = os.path.join(temp_dir, "nonexistent")

        # Ensure the directory doesn't exist
        assert not os.path.exists(nonexistent_dir)

        # Test that init raises typer.Exit with code 1
        with pytest.raises(typer.Exit) as exc_info:
            init(nonexistent_dir)

        assert exc_info.value.exit_code == 1


def test_init_non_git_directory() -> None:
    """Test that init command fails when directory is not a git repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory that exists but is not a git repository
        test_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(test_dir)

        # Ensure the directory exists but has no .git folder
        assert os.path.exists(test_dir)
        assert not os.path.exists(os.path.join(test_dir, ".git"))

        # Test that init raises typer.Exit with code 1
        with pytest.raises(typer.Exit) as exc_info:
            init(test_dir)

        assert exc_info.value.exit_code == 1


def test_init_successful_git_directory() -> None:
    """Test that init command succeeds in a git repository."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory and initialize it as a git repository
        test_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(test_dir)

        # Create .git directory to simulate a git repository
        git_dir = os.path.join(test_dir, ".git")
        os.makedirs(git_dir)

        # Ensure the directory exists and has a .git folder
        assert os.path.exists(test_dir)
        assert os.path.exists(git_dir)

        # Test that init succeeds without raising an exception
        init(test_dir)

        # Verify that expected files and directories were created
        assert os.path.exists(os.path.join(test_dir, "snippets.toml"))
        assert os.path.exists(os.path.join(test_dir, "snippets-schema.json"))
        assert os.path.exists(os.path.join(test_dir, "snippets"))