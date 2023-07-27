# CHANGELOG

## 0.7.2 (2023-07-27)

* [Feature] Added `push` and `tag` versioner configuration keys to `pyproject.toml` ([#63](https://github.com/ploomber/pkgmt/issues/63))

## 0.7.1 (2023-07-14)

* [Fix] Fixed `black` `--extend-exclude` override in `pyproject.toml`([#66](https://github.com/ploomber/pkgmt/issues/66))
* [Fix] Validation of keys in `pyproject.toml` ([#65](https://github.com/ploomber/pkgmt/issues/65))

## 0.7.0 (2023-07-11)

* [API Change] Support for projects containing `version` key in `pyproject.toml`. ([#58](https://github.com/ploomber/pkgmt/issues/58))
* [Fix] Fix bug when running git hook
* [Fix] Proper error message when version file is empty, or version string not found. Display version file location when inconsistent version in changelog ([#64](https://github.com/ploomber/pkgmt/issues/64))

## 0.6.2 (2023-06-30)

* [Feature] Added file path to `pkgmt lint` ([#56](https://github.com/ploomber/pkgmt/issues/56))
* [Feature] Clearer error when missing `pyproject.toml`
* [Feature] Added `--exclude` option to pkgmt `lint` and pkgmt `format` ([#55](https://github.com/ploomber/pkgmt/issues/55))

## 0.6.1 (2023-06-09)

* [Feature] Adds `python -m pkgmt.fail_if_not_modified` to test if certain paths in the repository have been modified

## 0.6.0 (2023-06-05)

* [API Change] Support for `pkgmt new` when argument contains `_` or `-`
* [Feature] Adds `python -m pkgmt.fail_if_modified` to test if certain paths in the repository have not been modified
* [Fix] `pkgmt setup` checks for `setup.py` file instead of `LICENSE`

## 0.5.1 (2023-05-19)

* [Feature] Add `tests/conftest.py` to package template ([#7](https://github.com/ploomber/pkgmt/issues/7))
* [Feature] Add `.github/pull_request_template.md` to package template ([#13](https://github.com/ploomber/pkgmt/issues/13))
* [Feature] Improvements to `.github/workflows/ci.yml` in package template ([#6](https://github.com/ploomber/pkgmt/issues/6))
* [Feature] Add `pyproject.toml` to package template ([#10](https://github.com/ploomber/pkgmt/issues/10))
* [Fix] Fix GitHub handle expansion when username contains `_` or `-`
* [Fix] Fix harcoded path in `MANIFEST.in` in package template ([#28](https://github.com/ploomber/pkgmt/issues/28))

## 0.5.0 (2023-04-28)

* [API Change] `pkgmt version` halts if there are uncommitted changes

## 0.4.2 (2023-04-28)

*No changes*

## 0.4.1 (2023-04-28)

*Never deployed due to a CI error*

* [Fix] locking ipython to 8.12.0 on py3.8
* [Fix] Fixing deprecations error

## 0.4.0 (2023-04-25)

* [API Change] `pkgmt version` checks out and pulls the main/master branch as the first step

## 0.3.1 (2023-04-24)

* [Fix] `pkgmt check-links` no longer reports `403` codes from `twitter.com` as errors

## 0.3.0 (2023-03-31)

* [Feature] Running `black --check .` when running `pkgmt lint`
* [Feature] Expanding GitHub handles when processing `CHANGELOG.md` files
* [Fix] Updates inaccurate confirmation message when running `pkgmt format`

## 0.2.11 (2023-03-30)

* [Feature] Test release, no changes

## 0.2.10 (2023-03-30)

* [Feature] Test release, no changes

## 0.2.9 (2023-03-30)

* [Feature] Test release, no changes

## 0.2.8 (2023-03-30)

* [Feature] Test release, no changes

## 0.2.7 (2023-03-30)

* [Feature] Adds `--yes` argument to `pkgmt release`

## 0.2.6 (2023-03-27)

* [Fix] Fixes error when running `pkgmt setup` on Windows

## 0.2.5 (2023-03-22)

* [Feature] Printing `package_name` at the end of the `setup` command

## 0.2.4 (2023-03-19)

* [Feature] Adds `--clean` option to `pkgmt doc`

## 0.2.3 (2023-03-19)

* [Fix] `pkgmt lint` exists with `1` return code if linting fails

## 0.2.2 (2023-03-19)

* [Feature] Adds `pkgmt format` and `pkgmt lint`

## 0.2.1 (2023-03-18)

* [Feature] Adds `pkgmt setup` and `pkgmt doc`

## 0.2.0 (2023-02-10)

* [API Change] `pkgmt version` pushes when `--no-tag` is passed

## 0.1.9 (2023-02-10)

* [Feature] Adds `--no-tag` option to `pkgmt version`
* [Feature] Adds `--target stable` option to `pkgmt version`

## 0.1.8 (2023-02-09)

* [Feature] Adds `pkgmt hook --run` for a one-time run
* [Feature] `pkgmt hook` Now runs `flake8` on notebooks via `nbqa`

## 0.1.7 (2023-02-09)

* [Feature] Adds `pkgmt.github` module with a function to determine the repository URL and branch for a readthedocs build

## 0.1.6 (2023-02-02)

* [Feature] `pkgmt release` prints confirmation message upon upload
* [Feature] Adds `--no-push` to `pkgmt version` to skip `git push`

## 0.1.5 (2023-01-28)

* [Fix] Moving back to master/main after uploading a package
* [Fix] No longer escaping characters in `code fences` when sorting `CHANGELOG`

## 0.1.4 (2023-01-17)

* [Feature] Adds `python -m pkgmt.dependencies` to find recently updated dependencies
* [Fix] Makes `mistune 3` an optional dependency

## 0.1.3 (2023-01-17)

* [Fix] Fixes `check_consistent_changelog_and_version` when `CHANGELOG.md` contains date

## 0.1.2 (2023-01-16)

* [Feature] Adds `pkgmt version`
* [Feature] Adds `pkgmt release`

## 0.1.1 (2023-01-15)

* [Feature] Adds `pkgmt check`
* [Feature] Adds `pkgmt hook`

## 0.1.0 (2023-01-06)

* Completing version string when missing components. (e.g., `1.0` -> `1.0.0`) ([#18](https://github.com/ploomber/pkgmt/issues/18))

## 0.0.18 (2023-01-03)

* `pkgmt check-links` prints invalid urls
* `pkgmt check-links` throttles requests to the same domain ([#19](https://github.com/ploomber/pkgmt/issues/19))

## 0.0.17 (2022-12-27)

* Adds `--only-404` option to `check-links` to only consider `404` HTTP codes as broken links

## 0.0.16 (2022-12-27)

* `pkgmt check-links` only hits URLs once

## 0.0.15 (2022-12-27)

* Faster `pkgmt check-links` (making a HEAD request instead of GET)

## 0.0.14 (2022-12-27)

* Improved support for `.ipynb` files in `pkgmt check-links`

## 0.0.13 (2022-12-26)

* `pkgmt check-links` reports HTTP response code

## 0.0.12 (2022-12-26)

* Faster `pkgmt check-links`
* `pkgmt check-links` ignores files not tracked by `git`

## 0.0.11 (2022-11-24)

* Ignores `src/__pycache__` when looking for package's `__init__.py`

## 0.0.10 (2022-07-22)

* Copying files when running `pkgmt test-md` in a temporary directory

## 0.0.9 (2022-07-20)

* Adds `pkgmt test-md` command to test `README.md` files

## 0.0.8 (2022-07-19)

* Adds sample GitHub Actions files
* Adds sample test
* Adds `pytest`, `flake8` and `invoke` as dev dependencies
* Adds sample `setup.cfg`

## 0.0.7 (2022-07-14)

* Adds support for projects that do not have a `setup.py` file

## 0.0.6 (2022-03-06)

* Adds `pkgmt new` command to create a new pre-configured package
* Allows packages with more than one folder under `src/`

## 0.0.5 (2022-02-14)

* Validate version string (first character must be numeric)

## 0.0.4 (2021-12-31)

* Adds `pkgmt` CLI
* Adds `pkgmt check-links` command to search for broken links

## 0.0.3 (2021-12-24)

* Integrates github expansion when creating a new version

## 0.0.2 (2021-12-24)

* Versioneer supports [pre-releases](https://www.python.org/dev/peps/pep-0440/#pre-releases)
* Aads config and changelog modules

## 0.0.1 (2021-10-17)

* First release
