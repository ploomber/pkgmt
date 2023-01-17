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
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, _Call
from datetime import datetime

import pytest

from pkgmt.versioner.versionersetup import VersionerSetup
from pkgmt.versioneer import VersionerNonSetup
from pkgmt import versioneer
from pkgmt.versioner import abstractversioner
from pkgmt.exceptions import ProjectValidationError


# FIXME: use unittest.mock.call instead of unittest.mock._Call
def _call(arg):
    """Shortcut for comparing call objects"""
    return _Call(((arg,),))


@pytest.fixture
def backup_another_package(root):
    old = os.getcwd()
    backup = tempfile.mkdtemp()
    backup_another_package = str(Path(backup, "backup-template"))
    path_to_templates = root / "tests" / "assets" / "another_package"
    shutil.copytree(str(path_to_templates), backup_another_package)

    os.chdir(path_to_templates)

    yield path_to_templates

    os.chdir(old)

    shutil.rmtree(str(path_to_templates))
    shutil.copytree(backup_another_package, str(path_to_templates))
    shutil.rmtree(backup)


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


def test_locate_package_and_readme(move_to_package_name):
    v = VersionerSetup()
    assert v.PACKAGE == Path("src", "package_name")
    assert v.path_to_changelog == Path("CHANGELOG.md")


def test_locate_package_and_readme_non_setup(move_to_another_package):
    v = VersionerNonSetup("app")
    assert v.PACKAGE == Path("app")
    assert v.path_to_changelog == Path("CHANGELOG.md")


def test_current_version(move_to_package_name):
    assert VersionerSetup().current_version() == "0.1dev"


def test_current_version_non_setup(move_to_another_package):
    assert VersionerNonSetup("app").current_version() == "0.1dev"


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
    monkeypatch.setattr(VersionerSetup, "current_version", lambda self: version_current)
    assert VersionerSetup().release_version() == version_release


def test_release_version_non_setup(move_to_another_package):
    assert VersionerNonSetup("app").release_version() == "0.1.0"


@pytest.mark.parametrize(
    "folder_name",
    [
        "__pycache__",
        "something.egg-info",
    ],
)
def test_ignore_special_folders(folder_name, backup_package_name):

    Path("src", folder_name).mkdir()

    name, package = VersionerSetup().find_package()

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
        [move_to_package_name, VersionerSetup, VersionerSetup()],
        [move_to_another_package, VersionerNonSetup, VersionerNonSetup("app")],
    ],
)
def test_bump_up_version(monkeypatch, version, version_new, move_to, attr, versioner):
    monkeypatch.setattr(attr, "current_version", lambda self: version)
    assert versioner.bump_up_version() == version_new


def test_commit_version_no_tag(backup_package_name, monkeypatch):
    v = VersionerSetup()

    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)

    v.commit_version(
        "0.2", msg_template="{package_name} release {new_version}", tag=False
    )

    assert mock.call_args_list == [
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", "package_name release 0.2"]),
    ]

    assert '__version__ = "0.2"' in (v.PACKAGE / "__init__.py").read_text()


def test_commit_version_no_tag_non_setup(backup_another_package, monkeypatch):
    v = VersionerNonSetup("app")

    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)

    v.commit_version(
        "0.2", msg_template="{package_name} release {new_version}", tag=False
    )

    assert mock.call_args_list == [
        _call(["git", "add", "--all"]),
        _call(["git", "status"]),
        _call(["git", "commit", "-m", "app release 0.2"]),
    ]

    assert '__version__ = "0.2"' in (v.PACKAGE / "_version.py").read_text()


def test_commit_version_tag(backup_package_name, monkeypatch):
    v = VersionerSetup()

    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)

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

    assert '__version__ = "0.2"' in (v.PACKAGE / "__init__.py").read_text()


def test_commit_version_tag_non_setup(backup_another_package, monkeypatch):
    v = VersionerNonSetup("app")

    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)

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

    assert '__version__ = "0.2"' in (v.PACKAGE / "_version.py").read_text()


def test_update_changelog_release_md(backup_package_name):
    v = VersionerSetup()
    v.update_changelog_release("0.1")
    today = datetime.now().strftime("%Y-%m-%d")
    assert (
        v.path_to_changelog.read_text()
        == f"# CHANGELOG\n\n## 0.1 ({today})\n\n* [Fix] Fixes #1"
    )


def test_update_changelog_release_md_non_setup(backup_another_package):
    v = VersionerNonSetup("app")
    v.update_changelog_release("0.1")
    today = datetime.now().strftime("%Y-%m-%d")
    assert (
        v.path_to_changelog.read_text()
        == f"# CHANGELOG\n\n## 0.1 ({today})\n\n* Fixes #1"
    )


def test_update_changelog_release_rst(backup_package_name):
    Path("CHANGELOG.md").unlink()
    Path("CHANGELOG.rst").write_text("CHANGELOG\n=========\n\n0.1dev\n------")

    v = VersionerSetup()
    v.update_changelog_release("0.1")
    today = datetime.now().strftime("%Y-%m-%d")
    assert (
        v.path_to_changelog.read_text()
        == f"CHANGELOG\n=========\n\n0.1 ({today})\n----------------"
    )


def test_update_changelog_release_rst_non_setup(backup_another_package):
    Path("CHANGELOG.md").unlink()
    Path("CHANGELOG.rst").write_text("CHANGELOG\n=========\n\n0.1dev\n------")

    v = VersionerNonSetup("app")
    v.update_changelog_release("0.1")
    today = datetime.now().strftime("%Y-%m-%d")
    assert (
        v.path_to_changelog.read_text()
        == f"CHANGELOG\n=========\n\n0.1 ({today})\n----------------"
    )


def test_add_changelog_new_dev_section_md(backup_package_name):
    v = VersionerSetup()
    v.add_changelog_new_dev_section("0.2dev")
    assert (
        v.path_to_changelog.read_text()
        == "# CHANGELOG\n\n## 0.2dev\n\n## 0.1dev\n\n* [Fix] Fixes #1"
    )


def test_add_changelog_new_dev_section_md_non_setup(backup_another_package):
    v = VersionerNonSetup("app")
    v.add_changelog_new_dev_section("0.2dev")
    assert (
        v.path_to_changelog.read_text()
        == "# CHANGELOG\n\n## 0.2dev\n\n## 0.1dev\n\n* Fixes #1"
    )


def test_add_changelog_new_dev_section_rst(backup_package_name):
    Path("CHANGELOG.md").unlink()
    Path("CHANGELOG.rst").write_text("CHANGELOG\n=========\n\n0.1dev\n------")

    v = VersionerSetup()
    v.add_changelog_new_dev_section("0.2dev")
    assert (
        v.path_to_changelog.read_text()
        == "CHANGELOG\n=========\n\n0.2dev\n------\n\n0.1dev\n------"
    )


def test_add_changelog_new_dev_section_rst_non_setup(backup_another_package):
    Path("CHANGELOG.md").unlink()
    Path("CHANGELOG.rst").write_text("CHANGELOG\n=========\n\n0.1dev\n------")

    v = VersionerNonSetup("app")
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
def test_release(backup_package_name, monkeypatch, submitted, stored, dev):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [submitted, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True)

    assert mock.call_args_list == [
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


def test_release_yes(backup_package_name, monkeypatch):
    mock = Mock()
    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)

    stored = "0.1.0"
    dev = "0.1.1dev"

    versioneer.version(yes=True)

    assert mock.call_args_list == [
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


@pytest.mark.parametrize(
    "submitted, stored, dev",
    [
        ["", "0.1.0", "0.1.1dev"],
        ["0.1", "0.1.0", "0.1.1dev"],
    ],
)
def test_release_non_setup(backup_another_package, monkeypatch, submitted, stored, dev):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [submitted, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True, version_package="app")

    assert mock.call_args_list == [
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
        "* Fixes [#1](https://github.com/edublancas/pkgmt/issues/1)"
    )


@pytest.mark.parametrize(
    "submitted, stored, dev",
    [
        ["1a10", "1.0.0a10", "1.0.0dev"],
        ["1.2b1", "1.2.0b1", "1.2.0dev"],
        ["1.2.5rc1", "1.2.5rc1", "1.2.5dev"],
    ],
)
def test_pre_release(backup_package_name, monkeypatch, submitted, stored, dev):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [submitted, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    monkeypatch.setattr(abstractversioner, "call", mock)

    versioneer.version(tag=True)

    assert mock.call_args_list == [
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


@pytest.mark.parametrize(
    "selected, stored, dev",
    [
        ["1a10", "1.0.0a10", "1.0.0dev"],
        ["1.2b1", "1.2.0b1", "1.2.0dev"],
        ["1.2.5rc1", "1.2.5rc1", "1.2.5dev"],
    ],
)
def test_pre_release_non_setup(
    backup_another_package, monkeypatch, selected, stored, dev
):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [selected, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True, version_package="app")

    assert mock.call_args_list == [
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
        "* Fixes [#1](https://github.com/edublancas/pkgmt/issues/1)"
    )


def test_release_with_no_changelog(backup_package_name, monkeypatch, capsys):
    Path("CHANGELOG.md").unlink()

    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = ["", "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True)

    captured = capsys.readouterr()
    assert "No CHANGELOG.{rst,md} found, skipping changelog editing..." in captured.out

    assert mock.call_args_list == [
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


def test_release_with_no_changelog_non_setup(
    backup_another_package, monkeypatch, capsys
):
    Path("CHANGELOG.md").unlink()

    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = ["", "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    versioneer.version(tag=True, version_package="app")

    captured = capsys.readouterr()
    assert "No CHANGELOG.{rst,md} found, skipping changelog editing..." in captured.out

    assert mock.call_args_list == [
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
def test_upload(backup_package_name, monkeypatch, production):
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
    ]

    mock_delete.assert_called_once_with(
        "dist", "build", str(Path("src", "package_name.egg-info"))
    )


@pytest.mark.parametrize("selected", ["y", "n", "y1.2"])
def test_invalid_version_string(backup_package_name, monkeypatch, selected):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [selected, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    with pytest.raises(ValueError) as excinfo:
        versioneer.version(tag=True)

    assert "(first character must be numeric)" in str(excinfo.value)


@pytest.mark.parametrize("selected", ["y", "n", "y1.2"])
def test_invalid_version_string_non_setup(
    backup_another_package, monkeypatch, selected
):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = [selected, "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

    with pytest.raises(ValueError) as excinfo:
        versioneer.version(tag=True, version_package="app")

    assert "(first character must be numeric)" in str(excinfo.value)


def test_sorts_changelog_entries(backup_package_name, monkeypatch):
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

    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = ["0.1", "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)
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


def test_checks_pending_deprecations(backup_package_name, monkeypatch):
    mock = Mock()
    mock_input = Mock()
    mock_input.side_effect = ["0.1", "y"]

    monkeypatch.setattr(versioneer, "call", mock)
    monkeypatch.setattr(abstractversioner, "call", mock)
    monkeypatch.setattr(versioneer, "_input", mock_input)

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

    with pytest.raises(ProjectValidationError) as excinfo:
        versioneer.version(tag=True)

    assert "Found the following pending deprecations" in str(excinfo.value)
    assert "This will be removed in version 0.3" in str(excinfo.value)


def test_picks_up_first_module_under_src(backup_package_name):
    Path("src", "z").mkdir()

    v = VersionerSetup()

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
