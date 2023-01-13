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
    assert changelog._get_latest_changelog_entries(text) == items


def test_check_latest_changelog_entries():
    assert changelog.check_latest_changelog_entries(
        """
# CHANGELOG

This is some text that should not [affect](https://ploomber.io)

## 0.1dev

- [API Change] Stuff
- [Doc] More stuff
- [Fix] More stuff
- [Feature] More stuff
"""
    )


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
        changelog.check_latest_changelog_entries(text)

    assert error in str(excinfo.value)


def test_check_latest_changelog_entries_ignore_if_empty():
    assert changelog.check_latest_changelog_entries(
        """
# CHANGELOG

## 0.2dev

## 0.1dev

- Stuff
- More stuff
"""
    )
