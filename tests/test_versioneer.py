"""
NOTE:
In previous versions (<=0.1.2), "ploomber scaffold" used our implementation
of versioneer.py, however, we switched to
https://github.com/python-versioneer/python-versioneer
because it's more granular and allows us to get a unique version per commit
automatically.

However ploomber, ploomber-scaffold and soopervisor projects still use
our own implementation. We are keeping these tests for now but at some point
we should migrate those projects to
https://github.com/python-versioneer/python-versioneer
and get rid of this.
"""

import subprocess
import os
from pathlib import Path
from unittest.mock import Mock, _Call
from datetime import datetime

import click
import pytest

from pkgmt import config
from pkgmt.versioner.versioner import Versioner
from pkgmt import versioneer

from pkgmt.versioner.util import (
    find_package_in_src,
    find_package_of_version_file,
    find_package_and_version_file,
    validate_version_file,
)
from pkgmt.versioner import versioner
from pkgmt.exceptions import ProjectValidationError, InvalidConfiguration


# FIXME: use unittest.mock.call instead of unittest.mock._Call
def _call(arg):
    """Shortcut for comparing call objects"""
    return _Call(((arg,),))


@pytest.fixture
def move_to_package_name(root):
    old = os.getcwd()
    p = root / "tests" / "assets" / "package_name"
    os.chdir(p)
    yield
    os.chdir(old)


@pytest.fixture
def move_to_another_package(root):
    old = os.getcwd()
    p = root / "tests" / "assets" / "another_package"
    os.chdir(p)
    yield
    os.chdir(old)


@pytest.fixture
def move_to_package_no_src(root):
    old = os.getcwd()
    p = root / "tests" / "assets" / "package_no_src"
    os.chdir(p)
    yield
    os.chdir(old)


@pytest.mark.parametrize(
    "tmp_package, package_name, version_file",
    [
        ["tmp_package_name", "package_name", "__init__.py"],
        ["tmp_another_package", "app", "_version.py"],
    ],
)
def test_commit_version_no_tag_from_config(
    tmp_package, package_name, version_file, monkeypatch, request
):
    tmp_package = request.getfixturevalue(tmp_package)
    v = Versioner.load()

    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)

    v.commit_version(
        "0.2", msg_template="{package_name} release {new_version}", tag=False
    )

    assert mock.call_args_list == [
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"{package_name} release 0.2"]),
        _call(["git", "push", "--no-verify"]),
    ]

    assert '__version__ = "0.2"' in (v.path_to_package / version_file).read_text()


def test_locate_package_and_readme(move_to_package_name):
    v = Versioner.load()
    assert v.path_to_package == Path("src", "package_name")
    assert v.path_to_changelog == Path("CHANGELOG.md")


def test_locate_package_and_readme_toml(move_to_another_package):
    v = Versioner.from_pyproject_toml()
    assert v.path_to_package == Path("app")
    assert v.path_to_changelog == Path("CHANGELOG.md")


def test_current_version(move_to_package_name):
    assert Versioner.load().current_version() == "0.1dev"


def test_current_version_toml(move_to_another_package):
    assert Versioner.from_pyproject_toml().current_version() == "0.1dev"


@pytest.mark.parametrize(
    "move_to_package, file_path",
    [
        [
            "move_to_package_name",
            "src/package_name/__init__.py",
        ],
        [
            "move_to_another_package",
            "app/_version.py",
        ],
    ],
)
def test_get_version_file_path(move_to_package, file_path, request):
    move_to_package = request.getfixturevalue(move_to_package)
    assert Versioner.load().get_version_file_path() == file_path


@pytest.mark.parametrize(
    "version_current, version_release",
    [
        ["0.1dev", "0.1.0"],
        ["0.1.0dev", "0.1.0"],
        ["0.2.1dev", "0.2.1"],
        ["1.2.6dev", "1.2.6"],
        ["1.2dev", "1.2.0"],
    ],
)
def test_release_version(
    monkeypatch, move_to_package_name, version_current, version_release
):
    monkeypatch.setattr(Versioner, "current_version", lambda self: version_current)
    assert Versioner.load().release_version() == version_release


def test_release_version_toml(move_to_another_package):
    assert Versioner.load().release_version() == "0.1.0"


@pytest.mark.parametrize(
    "folder_name",
    [
        "__pycache__",
        "something.egg-info",
    ],
)
def test_ignore_special_folders(folder_name, tmp_package_name):
    Path("src", folder_name).mkdir()

    name, package = find_package_in_src()
    assert name == "package_name"
    assert package == Path("src", "package_name")


@pytest.mark.parametrize(
    "version, version_new",
    [
        ["0.1", "0.1.1dev"],
        ["0.1.0", "0.1.1dev"],
        ["0.1.1", "0.1.2dev"],
        ["0.9", "0.9.1dev"],
        ["0.9.0", "0.9.1dev"],
        ["0.10a1", "0.10dev"],
        ["0.10b1", "0.10dev"],
        ["0.10rc1", "0.10dev"],
    ],
)
@pytest.mark.parametrize(
    "move_to, attr, versioner",
    [
        [
            move_to_package_name,
            Versioner,
            Versioner.load(),
        ],
        [
            move_to_another_package,
            Versioner,
            Versioner.load(),
        ],
    ],
)
def test_bump_up_version(monkeypatch, version, version_new, move_to, attr, versioner):
    monkeypatch.setattr(attr, "current_version", lambda self: version)
    assert versioner.bump_up_version() == version_new


def test_commit_version_no_tag(tmp_package_name, monkeypatch):
    v = Versioner.load()

    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)

    v.commit_version(
        "0.2", msg_template="{package_name} release {new_version}", tag=False
    )

    assert mock.call_args_list == [
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", "package_name release 0.2"]),
        _call(["git", "push", "--no-verify"]),
    ]

    assert '__version__ = "0.2"' in (v.path_to_package / "__init__.py").read_text()


def test_commit_version_no_tag_toml(tmp_another_package, monkeypatch):
    v = Versioner.load()

    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)

    v.commit_version(
        "0.2", msg_template="{package_name} release {new_version}", tag=False
    )

    assert mock.call_args_list == [
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", "app release 0.2"]),
        _call(["git", "push", "--no-verify"]),
    ]

    assert '__version__ = "0.2"' in (v.path_to_package / "_version.py").read_text()


def test_commit_version_tag(tmp_package_name, monkeypatch):
    v = Versioner.load()

    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)

    v.commit_version(
        "0.2", msg_template="{package_name} release {new_version}", tag=True
    )

    assert mock.call_args_list == [
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", "package_name release 0.2"]),
        _call(["git", "tag", "-a", "0.2", "-m", "package_name release 0.2"]),
        _call(["git", "push", "origin", "0.2", "--no-verify"]),
    ]

    assert '__version__ = "0.2"' in (v.path_to_package / "__init__.py").read_text()


def test_commit_version_tag_toml(tmp_another_package, monkeypatch):
    v = Versioner.load()

    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)

    v.commit_version(
        "0.2", msg_template="{package_name} release {new_version}", tag=True
    )

    assert mock.call_args_list == [
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", "app release 0.2"]),
        _call(["git", "tag", "-a", "0.2", "-m", "app release 0.2"]),
        _call(["git", "push", "origin", "0.2", "--no-verify"]),
    ]

    assert '__version__ = "0.2"' in (v.path_to_package / "_version.py").read_text()


def test_update_changelog_release_md(tmp_package_name):
    v = Versioner.load()
    v.update_changelog_release("0.1")
    today = datetime.now().strftime("%Y-%m-%d")
    assert (
        v.path_to_changelog.read_text()
        == f"# CHANGELOG\n\n## 0.1 ({today})\n\n* [Fix] Fixes #1"
    )


def test_update_changelog_release_md_toml(tmp_another_package):
    v = Versioner.load()
    v.update_changelog_release("0.1")
    today = datetime.now().strftime("%Y-%m-%d")
    assert (
        v.path_to_changelog.read_text()
        == f"# CHANGELOG\n\n## 0.1 ({today})\n\n* [Fix] Fixes #1"
    )


def test_update_changelog_release_rst(tmp_package_name):
    Path("CHANGELOG.md").unlink()
    Path("CHANGELOG.rst").write_text("CHANGELOG\n=========\n\n0.1dev\n------")

    v = Versioner.load()
    v.update_changelog_release("0.1")
    today = datetime.now().strftime("%Y-%m-%d")
    assert (
        v.path_to_changelog.read_text()
        == f"CHANGELOG\n=========\n\n0.1 ({today})\n----------------"
    )


def test_update_changelog_release_rst_toml(tmp_another_package):
    Path("CHANGELOG.md").unlink()
    Path("CHANGELOG.rst").write_text("CHANGELOG\n=========\n\n0.1dev\n------")

    v = Versioner.load()
    v.update_changelog_release("0.1")
    today = datetime.now().strftime("%Y-%m-%d")
    assert (
        v.path_to_changelog.read_text()
        == f"CHANGELOG\n=========\n\n0.1 ({today})\n----------------"
    )


def test_add_changelog_new_dev_section_md(tmp_package_name):
    v = Versioner.load()
    v.add_changelog_new_dev_section("0.2dev")
    assert (
        v.path_to_changelog.read_text()
        == "# CHANGELOG\n\n## 0.2dev\n\n## 0.1dev\n\n* [Fix] Fixes #1"
    )


def test_add_changelog_new_dev_section_md_toml(tmp_another_package):
    v = Versioner.load()
    v.add_changelog_new_dev_section("0.2dev")
    assert (
        v.path_to_changelog.read_text()
        == "# CHANGELOG\n\n## 0.2dev\n\n## 0.1dev\n\n* [Fix] Fixes #1"
    )


def test_add_changelog_new_dev_section_rst(tmp_package_name):
    Path("CHANGELOG.md").unlink()
    Path("CHANGELOG.rst").write_text("CHANGELOG\n=========\n\n0.1dev\n------")

    v = Versioner.load()
    v.add_changelog_new_dev_section("0.2dev")
    assert (
        v.path_to_changelog.read_text()
        == "CHANGELOG\n=========\n\n0.2dev\n------\n\n0.1dev\n------"
    )


def test_add_changelog_new_dev_section_rst_toml(tmp_another_package):
    Path("CHANGELOG.md").unlink()
    Path("CHANGELOG.rst").write_text("CHANGELOG\n=========\n\n0.1dev\n------")

    v = Versioner.load()
    v.add_changelog_new_dev_section("0.2dev")
    assert (
        v.path_to_changelog.read_text()
        == "CHANGELOG\n=========\n\n0.2dev\n------\n\n0.1dev\n------"
    )


@pytest.mark.parametrize(
    "submitted, stored, dev",
    [
        ["", "0.1.0", "0.1.1dev"],
        ["0.1", "0.1.0", "0.1.1dev"],
    ],
)
def test_version(tmp_package_name, monkeypatch, submitted, stored, dev):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [submitted, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True)

    assert mock.call_args_list == [
        _call(["git", "checkout", "main"]),
        _call(["git", "pull"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"package_name release {stored}"]),
        _call(["git", "tag", "-a", stored, "-m", f"package_name release {stored}"]),
        _call(["git", "push", "origin", stored, "--no-verify"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"Bumps up package_name to version {dev}"]),
        _call(["git", "push", "--no-verify"]),
    ]

    today = datetime.now().strftime("%Y-%m-%d")
    assert Path("CHANGELOG.md").read_text() == (
        f"# CHANGELOG\n\n## {dev}\n\n## {stored} ({today})\n\n"
        "* [Fix] Fixes [#1](https://github.com/edublancas/pkgmt/issues/1)\n"
    )


def test_version_no_push(tmp_package_name, monkeypatch):
    submitted, stored, dev = "0.1", "0.1.0", "0.1.1dev"
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [submitted, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(push=False)

    assert mock.call_args_list == [
        _call(["git", "checkout", "main"]),
        _call(["git", "pull"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"package_name release {stored}"]),
        _call(["git", "tag", "-a", stored, "-m", f"package_name release {stored}"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"Bumps up package_name to version {dev}"]),
    ]

    today = datetime.now().strftime("%Y-%m-%d")
    assert Path("CHANGELOG.md").read_text() == (
        f"# CHANGELOG\n\n## {dev}\n\n## {stored} ({today})\n\n"
        "* [Fix] Fixes [#1](https://github.com/edublancas/pkgmt/issues/1)\n"
    )


def test_version_yes(tmp_package_name, monkeypatch):
    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)

    stored = "0.1.0"
    dev = "0.1.1dev"

    versioneer.version(yes=True)

    assert mock.call_args_list == [
        _call(["git", "checkout", "main"]),
        _call(["git", "pull"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"package_name release {stored}"]),
        _call(["git", "tag", "-a", stored, "-m", f"package_name release {stored}"]),
        _call(["git", "push", "origin", stored, "--no-verify"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"Bumps up package_name to version {dev}"]),
        _call(["git", "push", "--no-verify"]),
    ]

    today = datetime.now().strftime("%Y-%m-%d")
    assert Path("CHANGELOG.md").read_text() == (
        f"# CHANGELOG\n\n## {dev}\n\n## {stored} ({today})\n\n"
        "* [Fix] Fixes [#1](https://github.com/edublancas/pkgmt/issues/1)\n"
    )


def test_version_target_stable(tmp_package_name, monkeypatch):
    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)

    stored = "0.1.0"

    versioneer.version(yes=True, target="stable")

    assert mock.call_args_list == [
        _call(["git", "checkout", "main"]),
        _call(["git", "pull"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"package_name release {stored}"]),
        _call(["git", "tag", "-a", stored, "-m", f"package_name release {stored}"]),
        _call(["git", "push", "origin", stored, "--no-verify"]),
    ]

    today = datetime.now().strftime("%Y-%m-%d")
    assert Path("CHANGELOG.md").read_text() == (
        f"# CHANGELOG\n\n## {stored} ({today})\n\n"
        "* [Fix] Fixes [#1](https://github.com/edublancas/pkgmt/issues/1)\n"
    )


@pytest.mark.parametrize(
    "submitted, stored, dev",
    [
        ["", "0.1.0", "0.1.1dev"],
        ["0.1", "0.1.0", "0.1.1dev"],
    ],
)
def test_version_toml(tmp_another_package, monkeypatch, submitted, stored, dev):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [submitted, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True)

    assert mock.call_args_list == [
        _call(["git", "checkout", "main"]),
        _call(["git", "pull"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"app release {stored}"]),
        _call(["git", "tag", "-a", stored, "-m", f"app release {stored}"]),
        _call(["git", "push", "origin", stored, "--no-verify"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"Bumps up app to version {dev}"]),
        _call(["git", "push", "--no-verify"]),
    ]

    today = datetime.now().strftime("%Y-%m-%d")
    assert Path("CHANGELOG.md").read_text() == (
        f"# CHANGELOG\n\n## {dev}\n\n## {stored} ({today})\n\n"
        "* [Fix] Fixes [#1](https://github.com/edublancas/pkgmt/issues/1)\n"
    )


@pytest.mark.parametrize(
    "submitted, stored, dev",
    [
        ["1a10", "1.0.0a10", "1.0.0dev"],
        ["1.2b1", "1.2.0b1", "1.2.0dev"],
        ["1.2.5rc1", "1.2.5rc1", "1.2.5dev"],
    ],
)
def test_version_pre_release(tmp_package_name, monkeypatch, submitted, stored, dev):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [submitted, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    monkeypatch.setattr(versioner, "call", mock)

    versioneer.version(tag=True)

    assert mock.call_args_list == [
        _call(["git", "checkout", "main"]),
        _call(["git", "pull"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"package_name release {stored}"]),
        _call(["git", "tag", "-a", stored, "-m", f"package_name release {stored}"]),
        _call(["git", "push", "origin", stored, "--no-verify"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"Bumps up package_name to version {dev}"]),
        _call(["git", "push", "--no-verify"]),
    ]

    # changelog must not change
    assert Path("CHANGELOG.md").read_text() == (
        "# CHANGELOG\n\n## 0.1dev\n\n"
        "* [Fix] Fixes [#1](https://github.com/edublancas/pkgmt/issues/1)\n"
    )


def test_version_error_if_extra_files(tmp_package_name, monkeypatch):
    submitted, _, _ = "0.1", "0.1.0", "0.1.1dev"
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [submitted, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    Path("some-file.txt").touch()
    Path("some-notebook.ipynb").touch()

    with pytest.raises(click.ClickException) as excinfo:
        versioneer.version()

    assert "pending files to commit" in str(excinfo.value)


@pytest.mark.parametrize(
    "selected, stored, dev",
    [
        ["1a10", "1.0.0a10", "1.0.0dev"],
        ["1.2b1", "1.2.0b1", "1.2.0dev"],
        ["1.2.5rc1", "1.2.5rc1", "1.2.5dev"],
    ],
)
def test_version_pre_release_toml(
    tmp_another_package, monkeypatch, selected, stored, dev
):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [selected, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True)

    assert mock.call_args_list == [
        _call(["git", "checkout", "main"]),
        _call(["git", "pull"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"app release {stored}"]),
        _call(["git", "tag", "-a", stored, "-m", f"app release {stored}"]),
        _call(["git", "push", "origin", stored, "--no-verify"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", f"Bumps up app to version {dev}"]),
        _call(["git", "push", "--no-verify"]),
    ]

    # changelog must not change
    assert Path("CHANGELOG.md").read_text() == (
        "# CHANGELOG\n\n## 0.1dev\n\n"
        "* [Fix] Fixes [#1](https://github.com/edublancas/pkgmt/issues/1)\n"
    )


def test_version_with_no_changelog(tmp_package_name, monkeypatch, capsys):
    Path("CHANGELOG.md").unlink()
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "commit"])

    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = ["", "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True)

    captured = capsys.readouterr()
    assert "No CHANGELOG.{rst,md} found, skipping changelog editing..." in captured.out

    assert mock.call_args_list == [
        _call(["git", "checkout", "main"]),
        _call(["git", "pull"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", "package_name release 0.1.0"]),
        _call(["git", "tag", "-a", "0.1.0", "-m", "package_name release 0.1.0"]),
        _call(["git", "push", "origin", "0.1.0", "--no-verify"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", "Bumps up package_name to version 0.1.1dev"]),
        _call(["git", "push", "--no-verify"]),
    ]


def test_version_with_no_changelog_toml(tmp_another_package, monkeypatch, capsys):
    Path("CHANGELOG.md").unlink()
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "delete-changelog"])

    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = ["", "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True)

    captured = capsys.readouterr()
    assert "No CHANGELOG.{rst,md} found, skipping changelog editing..." in captured.out

    assert mock.call_args_list == [
        _call(["git", "checkout", "main"]),
        _call(["git", "pull"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", "app release 0.1.0"]),
        _call(["git", "tag", "-a", "0.1.0", "-m", "app release 0.1.0"]),
        _call(["git", "push", "origin", "0.1.0", "--no-verify"]),
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", "Bumps up app to version 0.1.1dev"]),
        _call(["git", "push", "--no-verify"]),
    ]


@pytest.mark.parametrize("production", [False, True])
def test_upload(tmp_package_name, monkeypatch, production):
    mock = Mock()
    mock_input = Mock()
    mock_delete = Mock()
    mock_input.side_effect = ["y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)
    monkeypatch.setattr(versioneer, "delete_dirs", mock_delete)

    versioneer.upload(tag="0.1", production=production)

    upload_call = (
        _call(["twine", "upload", "dist/*"])
        if production
        else _call(
            [
                "twine",
                "upload",
                "--repository-url",
                "https://test.pypi.org/legacy/",
                "dist/*",
            ]
        )
    )

    assert mock.call_args_list == [
        _call(["git", "checkout", "0.1"]),
        _call(["python", "setup.py", "bdist_wheel", "sdist"]),
        upload_call,
        _call(["git", "checkout", "main"]),
    ]

    mock_delete.assert_called_once_with(
        "dist", "build", str(Path("src", "package_name.egg-info"))
    )


def test_upload_yes(tmp_package_name, monkeypatch):
    mock = Mock()
    mock_delete = Mock()

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioneer, "delete_dirs", mock_delete)

    versioneer.upload(tag="0.1", production=True, yes=True)

    assert mock.call_args_list == [
        _call(["git", "checkout", "0.1"]),
        _call(["python", "setup.py", "bdist_wheel", "sdist"]),
        _call(["twine", "upload", "dist/*"]),
        _call(["git", "checkout", "main"]),
    ]

    mock_delete.assert_called_once_with(
        "dist", "build", str(Path("src", "package_name.egg-info"))
    )


@pytest.mark.parametrize("selected", ["y", "n", "y1.2"])
def test_invalid_version_string(tmp_package_name, monkeypatch, selected):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [selected, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    with pytest.raises(ValueError) as excinfo:
        versioneer.version(tag=True)

    assert "(first character must be numeric)" in str(excinfo.value)


@pytest.mark.parametrize("selected", ["y", "n", "y1.2"])
def test_invalid_version_string_toml(tmp_another_package, monkeypatch, selected):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [selected, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    with pytest.raises(ValueError) as excinfo:
        versioneer.version(tag=True)

    assert "(first character must be numeric)" in str(excinfo.value)


def test_sorts_changelog_entries(tmp_package_name, monkeypatch):
    Path("CHANGELOG.md").write_text(
        """
# CHANGELOG

## 0.1dev

* [Fix] fix 1
* [Doc] doc 1
* [API Change] change 1
* [Feature] feature 1
"""
    )
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "commit"])

    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = ["0.1", "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True)
    today = datetime.now().strftime("%Y-%m-%d")

    assert (
        Path("CHANGELOG.md").read_text()
        == f"""\
# CHANGELOG

## 0.1.1dev

## 0.1.0 ({today})

* [API Change] change 1
* [Feature] feature 1
* [Fix] fix 1
* [Doc] doc 1
"""
    )


def test_checks_pending_deprecations(tmp_package_name, monkeypatch):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = ["0.1", "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    Path("CHANGELOG.md").write_text(
        """
# CHANGELOG

## 0.3dev

- [Fix] fix 1

"""
    )

    Path("src", "package_name", "__init__.py").write_text(
        """
__version__ = "0.3dev"
"""
    )

    Path("src", "package_name", "functions.py").write_text(
        '''
def do_stuff():
    """
    Notes
    -----
    .. deprecated:: 0.1
        This will be removed in version 0.3
    """
'''
    )

    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "commit"])

    with pytest.raises(ProjectValidationError) as excinfo:
        versioneer.version(tag=True)

    assert "Found the following pending deprecations" in str(excinfo.value)
    assert "This will be removed in version 0.3" in str(excinfo.value)


def test_checks_changelog(tmp_package_name, monkeypatch):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = ["0.1", "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    Path("CHANGELOG.md").write_text(
        """
# CHANGELOG

## 0.3dev

- fix 1

"""
    )

    Path("src", "package_name", "__init__.py").write_text(
        """
__version__ = "0.3dev"
"""
    )

    Path("src", "package_name", "functions.py").write_text(
        '''
def do_stuff():
    """
    Notes
    -----
    .. deprecated:: 0.1
        This will be removed in version 0.3
    """
'''
    )

    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "commit"])

    with pytest.raises(ProjectValidationError) as excinfo:
        versioneer.version(tag=True)

    assert "Found the following errors in the project" in str(excinfo.value)
    assert "[Invalid CHANGELOG]" in str(excinfo.value)


def test_picks_up_first_module_under_src(tmp_package_name):
    Path("src", "z").mkdir()

    v = Versioner.load()

    assert v.package_name == "package_name"


@pytest.mark.parametrize(
    "version, expected_error",
    [
        ["hello", "first character must be numeric"],
        ["", "invalid empty version string"],
    ],
)
def test_validate_version_string_error(version, expected_error):
    with pytest.raises(ValueError) as excinfo:
        versioneer.validate_version_string(version)

    assert expected_error in str(excinfo.value)


@pytest.mark.parametrize(
    "version, expected",
    [
        ["1.1.1", "1.1.1"],
        ["0.1.9", "0.1.9"],
        ["1", "1.0.0"],
        ["2.1", "2.1.0"],
        ["0.1", "0.1.0"],
    ],
)
def test_validate_version_string(version, expected):
    assert versioneer.validate_version_string(version) == expected


def test_find_package_in_src(move_to_package_name):
    package_name, path_to_package = find_package_in_src()
    assert path_to_package == Path("src", "package_name")
    assert package_name == "package_name"


def test_find_package_missing_src(move_to_package_no_src):
    with pytest.raises(NotADirectoryError) as excinfo:
        find_package_in_src()
    assert "Expected a directory at 'src' but it doesn't exist" in str(excinfo.value)


@pytest.mark.parametrize(
    (
        "version_file_path, expected_package_name, expected_path_to_package, "
        "expected_version_file_name"
    ),
    [
        ("app/_version.py", "app", "app", "_version.py"),
        ("app/nested/version.py", "nested", "app/nested", "version.py"),
        ("another_app/some_file.py", "another_app", "another_app", "some_file.py"),
    ],
)
def test_find_package_of_version_file(
    move_to_another_package,
    version_file_path,
    expected_package_name,
    expected_path_to_package,
    expected_version_file_name,
):
    package_name, path_to_package, version_file_name = find_package_of_version_file(
        version_file_path
    )

    assert package_name == expected_package_name
    assert path_to_package == Path(expected_path_to_package)
    assert version_file_name == expected_version_file_name


@pytest.mark.parametrize("version_file_path", ["", {}])
def test_version_file_empty(version_file_path):
    with pytest.raises(click.ClickException) as excinfo:
        validate_version_file(version_file_path)
    assert "Empty version file path in pyproject.toml." in str(excinfo.value)


def test_version_file_path_non_existent(move_to_another_package):
    with pytest.raises(click.ClickException) as excinfo:
        find_package_of_version_file("invalid/__init__.py")

    assert "Version file not found: invalid/__init__.py" in str(excinfo.value)


@pytest.mark.parametrize(
    "move_to_package, package_path, package_name, version_file",
    [
        [
            "move_to_package_name",
            Path("src", "package_name"),
            "package_name",
            "__init__.py",
        ]
    ],
)
def test_find_package_and_version_file(
    move_to_package, package_path, package_name, version_file, request
):
    move_to_package = request.getfixturevalue(move_to_package)
    package_name, PACKAGE, version_file_name = find_package_and_version_file()
    assert PACKAGE == package_path
    assert package_name == package_name
    assert version_file_name == version_file


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
def test_version_key_missing(tmp_package, version_file, error_path, request):
    tmp_package = request.getfixturevalue(tmp_package)
    version_file.write_text(
        """
        some_key = "0.1dev"
        """
    )
    with pytest.raises(click.ClickException) as excinfo:
        Versioner.load().current_version()
    assert (
        f"Please add version string in {error_path}, e.g., "
        "__version__ = '0.1dev'" in str(excinfo.value)
    )


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
def test_version_file_empty_contents(tmp_package, error_path, version_file, request):
    tmp_package = request.getfixturevalue(tmp_package)
    version_file.write_text("")
    with pytest.raises(click.ClickException) as excinfo:
        Versioner.load().current_version()
    assert (
        f"Please add version string in {error_path}, e.g., "
        "__version__ = '0.1dev'" in str(excinfo.value)
    )


@pytest.mark.parametrize(
    "tmp_package, version_file, error_path, text",
    [
        [
            "tmp_package_name",
            Path("src", "package_name", "__init__.py"),
            "src/package_name/__init__.py",
            """
            __version__ =
            """,
        ],
        [
            "tmp_another_package",
            Path("app", "_version.py"),
            "app/_version.py",
            "__version__ = 0.1dev",
        ],
    ],
)
def test_version_key_missing_value(
    tmp_package, version_file, error_path, text, request
):
    tmp_package = request.getfixturevalue(tmp_package)
    version_file.write_text(
        """
        __version__ =
        """
    )
    with pytest.raises(click.ClickException) as excinfo:
        Versioner.load().current_version()
    assert (
        f"Could not find __version__ value in {error_path}. "
        "Please add in the format __version__ = '0.1dev'" in str(excinfo.value)
    )


@pytest.mark.parametrize(
    "pyproject, error",
    [
        [
            '[tool.pkgmt]\ngithub = "repository/package"\n'
            'invalid_key = "some_value"',
            "Invalid keys in pyproject.toml file: invalid_key. "
            "Valid keys are: github, version, package_name, check_links",
        ],
        [
            '[tool.pkgmt]\ngithub = "repository/package"\n\n[tool.pkgmt.version]\n'
            'invalid_key = "some_value"',
            "Invalid version keys in pyproject.toml file: invalid_key. "
            "Valid version keys are: version_file, tag, push",
        ],
    ],
)
def test_validate_config(pyproject, error, tmp_another_package):
    Path("pyproject.toml").unlink()
    Path("pyproject.toml").write_text(pyproject)
    with pytest.raises(InvalidConfiguration) as excinfo:
        config.Config.from_file("pyproject.toml")
    assert error in str(excinfo.value)


@pytest.mark.parametrize(
    "pyproject, expected_tag, expected_push",
    [
        [
            '[tool.pkgmt]\ngithub = "repository/package"\n\n[tool.pkgmt.version]\n'
            'version_file = "/app/__init__.py"\npush = false',
            True,
            False,
        ],
        [
            '[tool.pkgmt]\ngithub = "repository/package"\n\n[tool.pkgmt.version]\n'
            'version_file = "/app/__init__.py"\ntag = false',
            False,
            True,
        ],
        [
            '[tool.pkgmt]\ngithub = "repository/package"\n\n[tool.pkgmt.version]\n'
            'version_file = "/app/__init__.py"\npush = false\ntag = false',
            False,
            False,
        ],
        [
            '[tool.pkgmt]\ngithub = "repository/package"\n\n[tool.pkgmt.version]\n'
            'version_file = "/app/__init__.py"\npush = false\ntag = true',
            True,
            False,
        ],
        [
            '[tool.pkgmt]\ngithub = "repository/package"\n\n[tool.pkgmt.version]\n'
            'version_file = "/app/__init__.py"',
            True,
            True,
        ],
    ],
)
def test_resolved_version_configurations(
    pyproject, tmp_another_package, expected_tag, expected_push
):
    Path("pyproject.toml").unlink()
    Path("pyproject.toml").write_text(pyproject)
    cfg = config.Config.from_file("pyproject.toml")
    assert cfg["version"]["push"] == expected_push
    assert cfg["version"]["tag"] == expected_tag


@pytest.mark.parametrize(
    "pyproject, error",
    [
        [
            '[tool.pkgmt]\ngithub = "repository/package"\n\n[tool.pkgmt.version]\n'
            'version_file = "/app/__init__.py"\npush = false\ntag = 1',
            "Invalid values for keys: tag. Expected boolean.",
        ],
        [
            '[tool.pkgmt]\ngithub = "repository/package"\n\n[tool.pkgmt.version]\n'
            'version_file = "/app/__init__.py"\npush = "false"\ntag = false',
            "Invalid values for keys: push. Expected boolean.",
        ],
    ],
)
def test_version_config_invalid(pyproject, error, tmp_another_package):
    Path("pyproject.toml").unlink()
    Path("pyproject.toml").write_text(pyproject)
    with pytest.raises(InvalidConfiguration) as excinfo:
        config.Config.from_file("pyproject.toml")
    assert error in str(excinfo.value)
