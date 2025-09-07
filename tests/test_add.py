import os
import tempfile
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

from typer.testing import CliRunner

from snippets.cli.main import app


def test_add_nonexisting_directory() -> None:
    """Test that add command fails when directory doesn't exist."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        nonexistent_dir = os.path.join(temp_dir, "nonexistent")

        # Ensure the directory doesn't exist
        assert not os.path.exists(nonexistent_dir)

        # Test that add command fails with exit code 1
        result = runner.invoke(app, ["add", "--repo", nonexistent_dir])
        assert result.exit_code == 1


def test_add_non_git_directory() -> None:
    """Test that add command fails when directory is not in a git repository."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory that exists but is not a git repository
        test_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(test_dir)

        # Ensure the directory exists but has no .git folder in any parent
        assert os.path.exists(test_dir)
        assert not os.path.exists(os.path.join(test_dir, ".git"))

        # Test that add command fails with exit code 1
        result = runner.invoke(app, ["add", "--repo", test_dir])
        assert result.exit_code == 1


def test_add_no_snippets_directory() -> None:
    """Test that add command fails when snippets directory doesn't exist."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory and initialize it as a git repository
        test_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(test_dir)

        # Create .git directory to simulate a git repository
        git_dir = os.path.join(test_dir, ".git")
        os.makedirs(git_dir)

        # Ensure the directory exists and has a .git folder but no snippets directory
        assert os.path.exists(test_dir)
        assert os.path.exists(git_dir)
        assert not os.path.exists(os.path.join(test_dir, "snippets"))

        # Test that add command fails with exit code 1
        result = runner.invoke(app, ["add", "--repo", test_dir])
        assert result.exit_code == 1


@patch("os.unlink")
@patch("os.isatty")
@patch("sys.stdin")
@patch("ulid.ULID")
@patch("builtins.open", new_callable=mock_open)
def test_add_with_piped_content(
    mock_file: MagicMock,
    mock_ulid: MagicMock,
    mock_stdin: MagicMock,
    mock_isatty: MagicMock,
    mock_unlink: MagicMock,
) -> None:
    """Test that add command works with piped content."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory and initialize it as a git repository
        test_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(test_dir)

        # Create .git directory and snippets directory
        git_dir = os.path.join(test_dir, ".git")
        snippets_dir = os.path.join(test_dir, "snippets")
        os.makedirs(git_dir)
        os.makedirs(snippets_dir)

        # Mock stdin to simulate piped content
        mock_isatty.return_value = False  # stdin is not a terminal (piped input)
        mock_stdin.read.return_value = "This is test content from stdin"

        # Mock ULID generation
        mock_ulid.return_value.test_ulid_id = "01HQTEST123456789"
        mock_ulid.return_value.__str__ = lambda self: "01HQTEST123456789"

        # Mock file operations
        mock_file.return_value.__enter__.return_value = mock_file.return_value

        # Test that add command succeeds
        result = runner.invoke(
            app, ["add", "--repo", test_dir], input="This is test content from stdin"
        )
        assert result.exit_code == 0

        # Verify that a file was opened for writing with the expected path
        expected_file_path = os.path.join(snippets_dir, "01HQTEST123456789.md")
        mock_file.assert_called_with(expected_file_path, "w")

        # Verify the content written to the file
        written_content = "".join(
            call.args[0] for call in mock_file.return_value.write.call_args_list
        )
        assert "---" in written_content
        assert "id: 01HQTEST123456789" in written_content
        assert "This is test content from stdin" in written_content

        # Verify that os.unlink was not called since we're using piped content (no temp file)
        mock_unlink.assert_not_called()


@patch("os.unlink")
@patch("os.isatty")
@patch("subprocess.run")
@patch("tempfile.NamedTemporaryFile")
@patch("ulid.ULID")
@patch("builtins.open", new_callable=mock_open)
def test_add_with_editor(
    mock_file: MagicMock,
    mock_ulid: MagicMock,
    mock_tempfile: MagicMock,
    mock_subprocess: MagicMock,
    mock_isatty: MagicMock,
    mock_unlink: MagicMock,
) -> None:
    """Test that add command works with editor."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory and initialize it as a git repository
        test_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(test_dir)

        # Create .git directory and snippets directory
        git_dir = os.path.join(test_dir, ".git")
        snippets_dir = os.path.join(test_dir, "snippets")
        os.makedirs(git_dir)
        os.makedirs(snippets_dir)

        # Mock stdin to simulate terminal input (not piped)
        mock_isatty.return_value = True

        # Mock ULID generation
        mock_ulid.return_value.test_ulid_id = "01HQTEST123456789"
        mock_ulid.return_value.__str__ = lambda self: "01HQTEST123456789"

        # Mock temporary file creation
        temp_file_path = "/tmp/test_temp_file.md"
        mock_temp_file = mock_tempfile.return_value.__enter__.return_value
        mock_temp_file.name = temp_file_path

        # Mock subprocess to simulate successful editor execution
        mock_subprocess.return_value = None

        # Mock file operations for reading temp file and writing snippet file
        def mock_open_side_effect(file_path: str, mode: str = "r") -> Any:
            if file_path == temp_file_path:
                mock_temp_read = mock_open(read_data="This is content from editor")
                return mock_temp_read.return_value
            else:
                return mock_file.return_value

        mock_file.side_effect = mock_open_side_effect

        # Test that add command succeeds
        result = runner.invoke(app, ["add", "--repo", test_dir])
        assert result.exit_code == 0

        # Verify that subprocess was called with the editor
        mock_subprocess.assert_called_once()
        assert "vim" in mock_subprocess.call_args[0][0]  # Default editor
        assert temp_file_path in mock_subprocess.call_args[0][0]

        # Verify that os.unlink was called to clean up the temp file
        mock_unlink.assert_called_once_with(temp_file_path)


@patch("os.isatty")
@patch("sys.stdin")
def test_add_with_empty_content(mock_stdin: MagicMock, mock_isatty: MagicMock) -> None:
    """Test that add command fails when no content is provided."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory and initialize it as a git repository
        test_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(test_dir)

        # Create .git directory and snippets directory
        git_dir = os.path.join(test_dir, ".git")
        snippets_dir = os.path.join(test_dir, "snippets")
        os.makedirs(git_dir)
        os.makedirs(snippets_dir)

        # Mock stdin to simulate empty piped content
        mock_isatty.return_value = False
        mock_stdin.read.return_value = ""

        # Test that add command fails with exit code 1
        result = runner.invoke(app, ["add", "--repo", test_dir], input="")
        assert result.exit_code == 1
