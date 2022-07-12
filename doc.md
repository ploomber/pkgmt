# Pkgmt

Pkgmt contains utilities for Python package management. 

### Project Structure
Currently, it supports two types of projects:

* Projects which contain a `setup.py` file. If multiple directories found in src folder the first is selected for versioning.

An example project structure is given below:

```
project_root
|
|__src
   |___dir1
       |___  __init__.py
   |
   |___dir2
|
|__CHANGELOG.md
|
|__pyproject.toml
```

`pyproject.toml` should contain an entry like:

```
[tool.pkgmt]
github = "project/repository" 
```
* Projects which do not contain a `setup.py` file. In this case the tool uses the `_version.py` file.

An example project structure is given below:

```
project_root
|
|__ app_one
|
|__ app_two
       |___  _version.py
|
|__CHANGELOG.md
|__config.yaml
```

`config.yaml` should contain an entry like:

```
pkgmt:
  github: project/repository
```

`_version.py` is placed in the directory whose versioning needs to be done through `pkgmt`.

### Setup

To setup dev environment, requires conda.

```
invoke setup 
```

### New version

Releasing a new version involves setting new stable version in `package_name/__init__.py`, updating header in `CHANGELOG` file and committing new version.

```
invoke new 
```

### Upload

Checks out a tag and uploads to PyPI.

```
invoke upload --tag <tag> --production <True/False>
```

`production` parameter is `True` by default.
