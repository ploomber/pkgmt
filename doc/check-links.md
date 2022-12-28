# Checking for broken links

## Configuration

Adds a `pyproject.toml` file in the root directory:

```toml
[tool.pkgmt.check_links]
extensions = ["md", "rst", "py", "ipynb"] # list of files to look for links
ignore_substrings = ["127.0.0.1"] # optional: ignore links with any of these substrings
```

## Checking

```{important}
This might report some HTTP codes as broken even when they're not
(e.g., we don't consider 405 as a broken link anymore). If there
are codes that we should not consider errors, please open
an [issue.](https://github.com/ploomber/pkgmt/issues/new)
```

```sh
pkgmt check-links
```
