# Checking for broken links

## Configuration

Adds a `pyproject.toml` file in the root directory:

```toml
[tool.pkgmt.check_links]
extensions = ["md", "rst", "py", "ipynb"] # list of files to look for links
ignore_substrings = ["127.0.0.1"] # optional: ignore links with any of these substrings
```

## Checking

```sh
pkgmt check-links
```