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
