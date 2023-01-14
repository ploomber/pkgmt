from pathlib import Path

import pytest

from pkgmt import changelog


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
            "Multiline\ntext (#123)",
            "Multiline\ntext ([#123]"
            "(https://github.com/edublancas/pkgmt/issues/123))",
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
def test_expand_github_from_text_yaml(tmp_empty, input, output):
    Path("config.yaml").write_text(
        """\
pkgmt:
  github: edublancas/pkgmt
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
            ["Stuff ", "More stuff ("],
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
            "['Stuff', 'More stuff']",
        ],
        [
            """
# CHANGELOG

## 0.1dev

- [API Change] Stuff
- More stuff
""",
            "['More stuff']",
        ],
    ],
)
def test_check_latest_changelog_entries_error(text, error):
    with pytest.raises(ValueError) as excinfo:
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


def test_check_consistent_dev_version(backup_package_name):
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
    with pytest.raises(ValueError, match="Expected a major version"):
        changelog.CHANGELOG(text).check_consistent_dev_version()


def test_check_consistent_changelog_and_version(backup_package_name):
    text = """
# CHANGELOG

## 0.1.1dev

- [API Change] some breaking change

## 0.1.0

- Stuff
- More stuff
"""
    with pytest.raises(
        ValueError,
        match="Inconsistent version. Version in  top section in "
        "CHANGELOG is 0.1.1dev. Version in __init__.py is 0.1dev",
    ):
        changelog.CHANGELOG(text).check_consistent_changelog_and_version()


def test_check(backup_package_name):
    Path("src", "package_name", "__init__.py").write_text(
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

    with pytest.raises(ValueError) as excinfo:
        changelog.CHANGELOG(text).check()

    assert "Expected a major version" in str(excinfo.value)
    assert "Found invalid items" in str(excinfo.value)
    assert "Inconsistent version" in str(excinfo.value)


def test_sort_last_section(backup_package_name):
    text = """
# CHANGELOG

## 0.1.1dev

- [Fix] fix 1
- [API Change] some breaking change
- [Doc] doc 1
- [Fix] fix 2

## 0.1.0

- Stuff
- More stuff
"""

    text_sorted = changelog.CHANGELOG(text).sort_last_section()

    assert (
        text_sorted
        == """
# CHANGELOG

## 0.1.1dev

- [API Change] some breaking change
- [Fix] fix 1
- [Fix] fix 2
- [Doc] doc 1

## 0.1.0

- Stuff
- More stuff
"""
    )
