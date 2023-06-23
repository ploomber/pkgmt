from unittest.mock import Mock
from pathlib import Path

from click.testing import CliRunner
import pytest

from pkgmt import cli


def test_check_links(tmp_empty):
    Path("pyproject.toml").write_text(
        """
[tool.pkgmt.check_links]
extensions = ["md"]
"""
    )

    Path("file.md").write_text("https://ploomber.io/broken")

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["check-links"])
    assert result.exit_code == 1
    assert "*** file.md ***\n(404) https://ploomber.io/broken\n" in result.output


@pytest.mark.parametrize(
    "args, yes, push, tag, target",
    [
        [["version"], False, True, True, None],
        [["version", "--yes"], True, True, True, None],
        [["version", "--yes", "--push"], True, True, True, None],
        [["version", "--push"], False, True, True, None],
        [["version", "--no-push"], False, False, True, None],
        [["version", "--no-push", "--tag"], False, False, True, None],
        [["version", "--push", "--no-tag"], False, True, False, None],
        [["version", "--target", "stable"], False, True, True, "stable"],
    ],
)
def test_version(tmp_package_name, monkeypatch, args, yes, push, tag, target):
    mock = Mock()

    monkeypatch.setattr(cli.versioneer, "version", mock)

    runner = CliRunner()
    runner.invoke(cli.cli, args)

    mock.assert_called_once_with(
        project_root=".", tag=tag, yes=yes, push=push, target=target
    )


def test_lint_pyproj(tmp_empty):
    Path("file.py").write_text(
        """
def stuff():
    pass



"""
    )

    runner = CliRunner()

    result = runner.invoke(cli.cli, ["lint"])
    assert result.exit_code == 1
    assert "Could not find project root" in result.output
    assert "Please add a pyproject.toml file in the root folder." in result.output


def test_lint_error(tmp_empty):
    Path("pyproject.toml").touch()
    Path("tmp_folder1").mkdir()
    Path("tmp_folder2").mkdir()
    Path("tmp_folder1", "file.py").write_text(
        """
def stuff():
    pass



"""
    )
    Path("tmp_folder2", "file.py").write_text("a = 1\n")

    runner = CliRunner()
    result_1 = runner.invoke(cli.cli, ["lint", "tmp_folder1"])
    result_2 = runner.invoke(cli.cli, ["lint", "tmp_folder2"])
    result_3 = runner.invoke(cli.cli, ["lint"])

    assert result_1.exit_code == 1
    assert result_2.exit_code == 0
    assert result_3.exit_code == 1

    assert "The following command failed: black --check" in result_1.output
    assert "The following command failed: flake8" in result_1.output
    assert "The following command failed: black --check" in result_3.output
    assert "The following command failed: flake8" in result_3.output


def test_format_error(tmp_empty):
    Path("pyproject.toml").touch()
    Path("tmp_folder1").mkdir()
    Path("tmp_folder1", "file.py").write_text(
        """
def stuff():
    pass



"""
    )
    Path("tmp_folder2").mkdir()
    Path("tmp_folder2", "file.py").write_text("a = 1\n")

    runner = CliRunner()
    result_1 = runner.invoke(cli.cli, ["format"])
    result_2 = runner.invoke(cli.cli, ["format", "tmp_folder2"])

    assert "Finished formatting with black!" in result_1.output
    assert "***black returned errors.***" in result_2.output
