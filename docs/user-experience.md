#  User Experience Design

## Setup
- A git repo needs to exist.
- Within the git repo, a few things would be required:
    - `snippets.toml` (this has the configuration for snippets)
    - `snippets/` folder to hold the snippets
    - git pre-commit hooks to validate that snippets match schema

The following command should be executed within the root directory of a git repo to create the setup.

```
snippets init .
```

## Configuration
The `snippets.toml` has the following configuration options:

`project` section has high level config options.
```
[project]
dirs = [dir1, dir2]  # default [snippets]
schema = "snippets-schema.json"
auto_update_properties = ["slug", "title", "created_at", "updated_at", "created_by", "updated_by"]
```

## Folder structure

```
snippets/
  - snippets1.md
  - snippets2.md
```

## Snippet format
YAML front matter followed by markdown.
```
id: <>
title: <>
...
--
snippet text
```

## git hooks
- `schema-validator.py` validates the schema file and ensure that it matches minimum constraints.
- `snippet-validator-.py` validates each modified snippet based on schema.
- `snippet-fixer.py` updates the `slug`, `title`, `created_by`, `updated_by`, `created_at` and `updated_at` fields.

## Schema

```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.example.com/snippet.schema.json",
  "title": "Snippet",
  "type": "object",
  "additionalProperties": false,
  "patternProperties": {
    "^x[_-].*$": {}
  },
  "properties": {
    "id": { "$ref": "#/$defs/ulid" },
    "slug": {
      "type": "string",
      "pattern": "^[a-z0-9][a-z0-9-]{2,63}$"
    },
    "lang": {
      "description": "BCP-47 language tag",
      "type": "string",
      "pattern": "^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*$",
      "default": "en"
    }
  },
  "required": [
    "id"
  ],
  "$defs": {
    "ulid": {
      "type": "string",
      "pattern": "^[0-9A-HJKMNP-TV-Z]{26}$"
    }
  }
}
```
