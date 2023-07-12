from pathlib import Path
import pytest

from pkgmt import changelog
from pkgmt.exceptions import ProjectValidationError


@pytest.mark.parametrize(
    "input,output",
    [
        (
            "Issue #535",
            "Issue [#535](https://github.com/edublancas/pkgmt/issues/535)",
        ),
        (
            "Multiline\ntext (#123)",
            "Multiline\ntext ([#123]"
            "(https://github.com/edublancas/pkgmt/issues/123))",
        ),
    ],
)
def test_replace_issue_numbers_with_links(input, output):
    assert (
        changelog._replace_issue_number_with_links(
            "https://github.com/edublancas/pkgmt/issues/", input
        )
        == output
    )


@pytest.mark.parametrize(
    "input,output",
    [
        (
            "Issue #535",
            "Issue [#535](https://github.com/edublancas/pkgmt/issues/535)",
        ),
        (
            "Issue [#535](https://github.com/edublancas/pkgmt/issues/535)",
            "Issue [#535](https://github.com/edublancas/pkgmt/issues/535)",
        ),
        (
            "Multiline\ntext (#123)",
            "Multiline\ntext ([#123]"
            "(https://github.com/edublancas/pkgmt/issues/123))",
        ),
        (
            "by @edublancas",
            "by [@edublancas](https://github.com/edublancas)",
        ),
        (
            "by @some_user-name",
            "by [@some_user-name](https://github.com/some_user-name)",
        ),
        (
            "by [@edublancas](https://github.com/edublancas)",
            "by [@edublancas](https://github.com/edublancas)",
        ),
    ],
)
def test_expand_github_from_text(tmp_empty, input, output):
    Path("pyproject.toml").write_text(
        """\
[tool.pkgmt]
github = "edublancas/pkgmt"
"""
    )

    Path("CHANGELOG.md").write_text(input)

    changelog.expand_github_from_changelog()

    assert output == Path("CHANGELOG.md").read_text()


@pytest.mark.parametrize(
    "text, items",
    [
        [
            """
# CHANGELOG

## 0.1dev

- Stuff
- More stuff
""",
            ["Stuff", "More stuff"],
        ],
        [
            """
# CHANGELOG

## 0.1dev

* Stuff #39
*    More stuff (#35)
""",
            ["Stuff #39", "More stuff (#35)"],
        ],
        [
            """
# CHANGELOG

## 0.1dev

- Stuff [#39](https://ploomber.io)
- More stuff ([#35](https://ploomber.io))
""",
            ["Stuff #39", "More stuff (#35)"],
        ],
    ],
)
def test_get_latest_changelog_entries(text, items):
    assert changelog.CHANGELOG(text).get_latest_changelog_section() == items


def test_check_latest_changelog_entries():
    assert changelog.CHANGELOG(
        """
# CHANGELOG

This is some text that should not [affect](https://ploomber.io)

## 0.1dev

- [API Change] Stuff
- [Doc] More stuff
- [Fix] More stuff
- [Feature] More stuff
"""
    ).check_latest_changelog_entries()


@pytest.mark.parametrize(
    "text, error",
    [
        [
            """
# CHANGELOG

## 0.1dev

- Stuff
- More stuff
""",
            "'Stuff', 'More stuff'",
        ],
        [
            """
# CHANGELOG

## 0.1dev

- [API Change] Stuff
- More stuff
""",
            "'More stuff'",
        ],
    ],
)
def test_check_latest_changelog_entries_error(text, error):
    with pytest.raises(ProjectValidationError) as excinfo:
        changelog.CHANGELOG(text).check_latest_changelog_entries()

    assert error in str(excinfo.value)


def test_check_latest_changelog_entries_ignore_if_empty():
    assert changelog.CHANGELOG(
        """
# CHANGELOG

## 0.2dev

## 0.1dev

- Stuff
- More stuff
"""
    ).check_latest_changelog_entries()


def test_check_consistent_dev_version(tmp_package_name):
    Path("src", "package_name", "__init__.py").write_text(
        """
__version__ = "0.1.1dev"
"""
    )

    text = """
# CHANGELOG

## 0.1.1dev

- [API Change] some breaking change

## 0.1.0

- Stuff
- More stuff
"""
    with pytest.raises(ProjectValidationError, match="Expected a major version"):
        changelog.CHANGELOG(text).check_consistent_dev_version()


@pytest.mark.parametrize(
    "init, subheading, tmp_package, version_file, error_path",
    [
        [
            "0.1dev",
            "0.1.1dev",
            "tmp_package_name",
            Path("src", "package_name", "__init__.py"),
            "src/package_name/__init__.py",
        ],
        [
            "0.1",
            "0.1.1",
            "tmp_package_name",
            Path("src", "package_name", "__init__.py"),
            "src/package_name/__init__.py",
        ],
        [
            "0.1.1",
            "0.1.1 some stuff",
            "tmp_package_name",
            Path("src", "package_name", "__init__.py"),
            "src/package_name/__init__.py",
        ],
        [
            "0.1dev",
            "0.1.1dev",
            "tmp_another_package",
            Path("app", "_version.py"),
            "app/_version.py",
        ],
        [
            "0.1",
            "0.1.1",
            "tmp_another_package",
            Path("app", "_version.py"),
            "app/_version.py",
        ],
        [
            "0.1.1",
            "0.1.1 some stuff",
            "tmp_another_package",
            Path("app", "_version.py"),
            "app/_version.py",
        ],
    ],
)
def test_check_consistent_changelog_and_version(
    tmp_package, init, subheading, version_file, error_path, request
):
    tmp_package = request.getfixturevalue(tmp_package)
    version_file.write_text(
        f"""
__version__ = "{init}"
"""
    )

    text = f"""
# CHANGELOG

## {subheading}

- [API Change] some breaking change

## 0.1.0

- Stuff
- More stuff
"""
    with pytest.raises(ProjectValidationError) as excinfo:
        changelog.CHANGELOG(text).check_consistent_changelog_and_version()

    assert "[Inconsistent version]" in str(excinfo.value)
    assert f"version in {error_path} is" in str(excinfo.value)
    assert init in str(excinfo.value)
    assert subheading in str(excinfo.value)


@pytest.mark.parametrize(
    "init, subheading",
    [
        ["0.1dev", "0.1dev"],
        ["0.1.0dev", "0.1.0dev"],
        ["0.1.0", "0.1.0"],
        ["0.1.0", "0.1.0 (2023-01-16)"],
    ],
)
def test_check_consistent_changelog_and_version_ignores_date(
    tmp_package_name, init, subheading
):
    Path("src", "package_name", "__init__.py").write_text(
        f"""
__version__ = "{init}"
"""
    )

    text = f"""
# CHANGELOG

## {subheading}

- [API Change] some breaking change

## 0.0.1

- Stuff
- More stuff
"""

    changelog.CHANGELOG(text).check_consistent_changelog_and_version()


@pytest.mark.parametrize(
    "tmp_package, version_file, error_path",
    [
        [
            "tmp_package_name",
            Path("src", "package_name", "__init__.py"),
            "src/package_name/__init__.py",
        ],
        [
            "tmp_another_package",
            Path("app", "_version.py"),
            "app/_version.py",
        ],
    ],
)
def test_check(tmp_package, error_path, version_file, request):
    tmp_package = request.getfixturevalue(tmp_package)
    version_file.write_text(
        """
__version__ = "0.1.2dev"
"""
    )

    text = """
# CHANGELOG

## 0.1.1dev

- [API Change] some breaking change
- Some other change

## 0.1.0

- Stuff
- More stuff
"""

    with pytest.raises(ProjectValidationError) as excinfo:
        changelog.CHANGELOG(text).check()

    assert "[Unexpected version]" in str(excinfo.value)
    assert "[Invalid CHANGELOG]" in str(excinfo.value)
    assert "[Inconsistent version]" in str(excinfo.value)
    assert f"version in {error_path} is" in str(excinfo.value)


@pytest.mark.parametrize(
    "text, expected",
    [
        [
            """\
# CHANGELOG

## 0.1.1dev

- [Fix] fix 1, pins `package<2`
- [API Change] some breaking change in `some_module`
- [Doc] doc 1
- [Fix] fix 2

## 0.1.0

- Stuff
- More stuff
""",
            """\
# CHANGELOG

## 0.1.1dev

- [API Change] some breaking change in `some_module`
- [Fix] fix 1, pins `package<2`
- [Fix] fix 2
- [Doc] doc 1

## 0.1.0

- Stuff
- More stuff
""",
        ],
        [
            """\
# CHANGELOG

## 0.1.1dev

## 0.1.0
""",
            """\
# CHANGELOG

## 0.1.1dev

## 0.1.0
""",
        ],
    ],
    ids=["unsorted", "empty"],
)
def test_sort_last_section(text, expected):
    text_sorted = changelog.CHANGELOG(text).sort_last_section()

    assert text_sorted == expected
