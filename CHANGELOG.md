# CHANGELOG

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
