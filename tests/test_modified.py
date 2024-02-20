import pytest
import subprocess

from pkgmt import fail_if_modified, fail_if_not_modified, fail_if_invalid_changelog
from pathlib import Path


@pytest.mark.parametrize(
    "base_branch, exclude_path, returncode",
    [
        [
            "main",
            ["test_doc1"],
            1,
        ],
        [
            "main",
            ["test_doc1", "test_doc2"],
            0,
        ],
    ],
)
def test_check_modified_ex(tmp_package_modi, base_branch, exclude_path, returncode):
    assert (
        fail_if_modified.check_modified(base_branch, exclude_path, debug=True)
        == returncode
    )


def test_check_modified_ex_2(tmp_package_modi_2):
    assert fail_if_modified.check_modified("main", ["doc"], debug=True) == 0


@pytest.mark.parametrize(
    "base_branch, include_path, returncode",
    [
        [
            "main",
            ["test_doc1"],
            0,
        ],
        [
            "main",
            ["test_doc1", "test_doc2"],
            0,
        ],
        [
            "main",
            ["src"],
            1,
        ],
        [
            "main",
            ["test_doc1", "test_doc2", "src"],
            1,
        ],
    ],
)
def test_check_modified_in(tmp_package_modi, base_branch, include_path, returncode):
    assert (
        fail_if_not_modified.check_modified(base_branch, include_path, debug=True)
        == returncode
    )


@pytest.mark.parametrize(
    "base_branch, include_path, returncode",
    [
        [
            "main",
            [str(Path("doc", "another.txt"))],
            0,
        ],
        [
            "main",
            [str(Path("something", "file.txt"))],
            1,
        ],
    ],
)
def test_check_modified_in_2(tmp_package_modi_2, base_branch, include_path, returncode):
    assert (
        fail_if_not_modified.check_modified(base_branch, include_path, debug=True)
        == returncode
    )


# @pytest.mark.parametrize("contents", ["""
# # CHANGELOG
#
# ## 0.1dev
#
# * [Fix] Fixes #1
# * [Feature] Added feature 1
# """
# ])
def test_check_modified_changelog(tmp_package_changelog):
    Path("CHANGELOG.md").write_text(
        """
# CHANGELOG

## 0.1dev

* [Fix] Fixes #1
* [Feature] Added feature 1
"""
    )
    subprocess.run(["git", "add", "CHANGELOG.md"])
    subprocess.run(["git", "commit", "-m", "changelog_modified"])
    assert fail_if_invalid_changelog.check_modified("main", debug=True) == 0


@pytest.mark.parametrize(
    "contents, message",
    [
        (
            """
# CHANGELOG

## 0.1dev

* [Fix] Fixes #1


""",
            "CHANGELOG.md has not been modified with respect to 'main'",
        ),
        (
            """
# CHANGELOG

## 0.1dev

* [Fix] Fixes #1

""",
            "CHANGELOG.md has not been modified with respect to 'main'",
        ),
        (
            """
# CHANGELOG

## 0.0.1dev

* [Fix] Fixes #1

""",
            "Latest section in CHANGELOG.md not up-to-date. "
            "Latest section in main: 0.1dev",
        ),
        (
            """
# CHANGELOG

## 0.1dev

* [Fix] Fixes #1

## 0.0.1

* [Feature] Some feature

""",
            "Entry '* [Feature] Some feature' should be added to section 0.1dev",
        ),
        (
            """
# CHANGELOG

## 0.1dev

* [Fix] Fixes #2

""",
            "These entries have been removed: * [Fix] Fixes #1. "
            "Please revert the changes.",
        ),
    ],
    ids=["blanks", "no-change", "outdated-header", "incorrect-section", "removal"],
)
def test_check_modified_changelog_error(
    tmp_package_changelog, contents, message, capsys
):
    Path("CHANGELOG.md").write_text(contents)
    subprocess.run(["git", "add", "CHANGELOG.md"])
    subprocess.run(["git", "commit", "-m", "changelog_modified"])
    assert fail_if_invalid_changelog.check_modified("main", debug=True) == 1
    assert message in capsys.readouterr().out


def test_check_modified_changelog_error_file_added(tmp_package_changelog, capsys):
    Path("some_file.txt").write_text("content")
    subprocess.run(["git", "add", "some_file.txt"])
    subprocess.run(["git", "commit", "-m", "added file"])
    assert fail_if_invalid_changelog.check_modified("main", debug=True) == 1
    out = capsys.readouterr().out
    assert "CHANGELOG.md has not been modified with respect to 'main'" in out
