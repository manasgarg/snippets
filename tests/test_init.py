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
        assert os.path.exists(
            os.path.join(test_dir, "scripts", "snippets-validator.py")
        )
        assert os.path.exists(os.path.join(test_dir, ".pre-commit-config.yaml"))


def test_init_with_existing_precommit_config() -> None:
    """Test that init command properly updates existing .pre-commit-config.yaml."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory and initialize it as a git repository
        test_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(test_dir)

        # Create .git directory to simulate a git repository
        git_dir = os.path.join(test_dir, ".git")
        os.makedirs(git_dir)

        # Create an existing .pre-commit-config.yaml file
        precommit_config_path = os.path.join(test_dir, ".pre-commit-config.yaml")
        existing_config = """repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: local
    hooks:
      - id: some-other-hook
        name: some-other-hook
        entry: echo "test"
        language: system
"""
        with open(precommit_config_path, "w") as f:
            f.write(existing_config)

        # Test that init succeeds without raising an exception
        init(test_dir)

        # Verify that expected files and directories were created
        assert os.path.exists(os.path.join(test_dir, "snippets.toml"))
        assert os.path.exists(os.path.join(test_dir, "snippets-schema.json"))
        assert os.path.exists(os.path.join(test_dir, "snippets"))
        assert os.path.exists(
            os.path.join(test_dir, "scripts", "snippets-validator.py")
        )
        assert os.path.exists(precommit_config_path)

        # Verify that the existing config was updated with the snippets validator hook
        import yaml

        with open(precommit_config_path) as f:
            config = yaml.safe_load(f)

        # Find the local repo
        local_repo = None
        for repo in config["repos"]:
            if repo.get("repo") == "local":
                local_repo = repo
                break

        assert local_repo is not None
        assert "hooks" in local_repo

        # Check that both the existing hook and the new snippets validator hook exist
        hook_ids = [hook.get("id") for hook in local_repo["hooks"]]
        assert "some-other-hook" in hook_ids
        assert "snippets-validator" in hook_ids

        # Verify the snippets validator hook has correct configuration
        snippets_hook = None
        for hook in local_repo["hooks"]:
            if hook.get("id") == "snippets-validator":
                snippets_hook = hook
                break

        assert snippets_hook is not None
        assert snippets_hook["name"] == "snippets-validator"
        assert snippets_hook["entry"] == "python scripts/snippets-validator.py"
        assert snippets_hook["language"] == "system"
        assert snippets_hook["files"] == r"^snippets/.*\.md$"
        assert snippets_hook["pass_filenames"] is True


def test_init_with_existing_precommit_config_no_local_repo() -> None:
    """Test init with existing .pre-commit-config.yaml that doesn't have a local repo section."""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_dir = os.path.join(temp_dir, "test_project")
        os.makedirs(test_dir)

    # Create .git directory to make it a valid git repo
    git_dir = os.path.join(test_dir, ".git")
    os.makedirs(git_dir)

    # Create existing .pre-commit-config.yaml without local repo
    precommit_config_path = os.path.join(test_dir, ".pre-commit-config.yaml")
    existing_config = """repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
"""
    with open(precommit_config_path, "w") as f:
        f.write(existing_config)

    # Test that init succeeds without raising an exception
    init(test_dir)

    # Verify that expected files and directories were created
    assert os.path.exists(os.path.join(test_dir, "snippets.toml"))
    assert os.path.exists(os.path.join(test_dir, "snippets-schema.json"))
    assert os.path.exists(os.path.join(test_dir, "snippets"))
    assert os.path.exists(os.path.join(test_dir, "scripts", "snippets-validator.py"))
    assert os.path.exists(precommit_config_path)

    # Verify that the existing config was updated with a new local repo containing the snippets validator hook
    import yaml

    with open(precommit_config_path) as f:
        config = yaml.safe_load(f)

    # Find the local repo (should have been created)
    local_repo = None
    for repo in config["repos"]:
        if repo.get("repo") == "local":
            local_repo = repo
            break

    assert local_repo is not None
    assert "hooks" in local_repo

    # Check that the snippets validator hook exists
    hook_ids = [hook.get("id") for hook in local_repo["hooks"]]
    assert "snippets-validator" in hook_ids

    # Verify the snippets validator hook has correct configuration
    snippets_hook = None
    for hook in local_repo["hooks"]:
        if hook.get("id") == "snippets-validator":
            snippets_hook = hook
            break

    assert snippets_hook is not None
    assert snippets_hook["name"] == "snippets-validator"
    assert snippets_hook["entry"] == "python scripts/snippets-validator.py"
    assert snippets_hook["language"] == "system"
    assert snippets_hook["files"] == r"^snippets/.*\.md$"
    assert snippets_hook["pass_filenames"] is True

    # Verify that existing repos are still present
    repo_urls = [repo.get("repo") for repo in config["repos"]]
    assert "https://github.com/psf/black" in repo_urls
    assert "local" in repo_urls
