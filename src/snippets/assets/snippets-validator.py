#!/usr/bin/env python3
"""
Validation script for markdown snippets with YAML frontmatter.
This script is designed to be used with pre-commit framework.
"""

import argparse
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any


def extract_frontmatter(content: str) -> str | None:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None

    pattern = r"^---\s*\n(.*?)\n---\s*$"
    match = re.match(pattern, content, re.MULTILINE | re.DOTALL)

    if not match:
        return None

    return match.group(1)


def validate_ulid_format(ulid_str: str) -> bool:
    """Validate ULID format (26 characters, specific character set)."""
    ulid_pattern = r"^[0-9A-HJKMNP-TV-Z]{26}$"
    return bool(re.match(ulid_pattern, ulid_str, re.IGNORECASE))


def find_repo_root() -> Path:
    """Find the repository root by looking for .git directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()


def load_schema(schema_path: Path) -> dict[str, Any]:
    """Load JSON schema from file."""
    try:
        with open(schema_path) as f:
            return dict(json.load(f))
    except FileNotFoundError:
        print(f"Error: Schema file not found: {schema_path}")
        print("Please create a snippets-schema.json file in your repository root")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in schema file {schema_path}: {e}")
        sys.exit(1)


def validate_markdown_file(filepath: Path, schema: dict[str, Any]) -> list[str]:
    """Validate a single markdown file against requirements."""
    errors: list[str] = []

    # Import here to ensure dependencies are available
    try:
        import jsonschema
        import yaml
    except ImportError as e:
        return [f"Missing dependency: {e}"]

    # Read file content
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Error reading file {filepath}: {e}"]

    # Extract and validate frontmatter
    frontmatter_str = extract_frontmatter(content)
    if frontmatter_str is None:
        errors.append("No valid YAML frontmatter found")
        return errors

    # Parse YAML frontmatter
    try:
        frontmatter: dict[str, Any] = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML in frontmatter: {e}")
        return errors

    # Validate against JSON schema
    try:
        jsonschema.validate(instance=frontmatter, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(f"Schema validation failed: {e.message}")
    except jsonschema.SchemaError as e:
        errors.append(f"Schema error: {e.message}")

    # Extract ULID from filename
    filename_ulid = filepath.stem  # filename without extension

    # Validate ULID format
    if not validate_ulid_format(filename_ulid):
        errors.append(
            f"Filename '{filepath.name}' does not follow <ulid>.md format (invalid ULID)"
        )

    # Check if ULID matches id in frontmatter
    if frontmatter and "id" not in frontmatter:
        errors.append("Missing 'id' field in frontmatter")
    elif frontmatter and frontmatter.get("id") != filename_ulid:
        errors.append(
            f"ULID mismatch: filename has '{filename_ulid}' "
            f"but frontmatter id is '{frontmatter.get('id')}'"
        )

    return errors


def main(argv: Sequence[str] | None = None) -> int:
    """Main function for pre-commit hook."""
    parser = argparse.ArgumentParser(
        description="Validate markdown files in snippets directory"
    )
    parser.add_argument("filenames", nargs="*", help="Filenames to validate")
    args = parser.parse_args(argv)

    if not args.filenames:
        return 0

    # Find repository root and schema path
    repo_root = find_repo_root()
    schema_path = repo_root / "snippets-schema.json"

    # Load schema once
    schema = load_schema(schema_path)

    # Track if any errors occurred
    exit_code = 0

    # Validate each file
    for filename in args.filenames:
        filepath = Path(filename)

        # Only validate .md files in snippets directory
        if not ("snippets" in filepath.parts and filepath.suffix == ".md"):
            continue

        errors = validate_markdown_file(filepath, schema)

        if errors:
            exit_code = 1
            print(f"❌ {filepath}:")
            for error in errors:
                print(f"   {error}")
        else:
            print(f"✅ {filepath}: Valid")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
