# Versioning a project

Executing `pkgmt version` will modify the `__version__` string in the version file, and the headers in `CHANGELOG.md`. 
The version file path will be mentioned either in the `pyproject.toml` file, or in the `setup.py` file by default.

### Project Structure
Currently, `pkgmt` supports versioning in two types of projects:

* If version file path is not specified in the `pyproject.toml` file, the versioner looks for an `__init__.py` file by traversing the directories under `src/`. 
If multiple directories are found in `src` folder the first is selected for versioning.

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

The `__init__.py` file should contain the version string as shown below:

```python
__version__ = "0.1dev"
```

* Projects in which `version` key is present in the `pyproject.toml` file. This version file takes precedence over any existing `__init__.py` file inside one of the `src\` subdirectories. Note that this version file can also be a `__init__.py` file inside a specific directory.
The `pyproject.toml` should contain an entry like:

```
[tool.pkgmt]
github = "project/repository" 
version = {version_file = "/path/to/version_file.py"}
```

An example project structure is given below:

```
project_root
|
|__ app_one
|
|__ app_two
       |__ __init__.py
|
|__CHANGELOG.md
|__pyproject.toml
```

`pyproject.toml` should contain an entry like:

```
[tool.pkgmt]
github = "project/repository"
version = {version_file = 'app_two/__init__.py'}
```

#### Version in pyproject.toml

The `version` key in the `pyproject.toml` file can be used to specify the following:

* `version_file` : path of the file in which the `__version__` string is specified.
* `tag`: Specifies whether to tag the commit with the stable version. Available options: `true` / `false`.
* `push` : Specifies whether to push the changes to the remote repository. Available options: `true` / `false`.

Note that `tag` and `push` are optional. If passed, the options override the default value of `True`.

### New version

Releasing a new version involves the following steps:
* Set new stable version in `src/package_name/__init__.py` (if `version` key is not present in `pyproject.toml`) / `package_name/version_file.py` (if `version` key is present in `pyproject.toml`).
* Update header in `CHANGELOG` file and ask to review.
* Create commit for new version, create git tag, and push.
* Set new development version in `src/package_name/__init__.py` (if `version` key is not present in `pyproject.toml`) / `package_name/version_file.py` (if `version` key is present in `pyproject.toml`), and CHANGELOG.
* Commit new development version and push

Run the below command inside the project which needs to be versioned:

```
pkgmt version
```

### Upload

Checks out a tag and uploads to `PyPI`.

```
pkgmt release --tag <tag>
```

The command also accepts a `--production` flag, which when passed publishes the project to `PyPI`, else to the `PyPI test server`.

