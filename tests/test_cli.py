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


def test_pyproj(tmp_empty):
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


@pytest.mark.parametrize(
    "command,exit_code",
    [
        [
            "lint tmp_folder1",
            1,
        ],
        ["lint tmp_folder2", 0],
        ["lint", 1],
        ["lint . -e tmp_folder1", 0],
        ["lint . -e tmp_folder1 -e tmp_folder2", 0],
        ["lint . -e tmp_folder2", 1],
    ],
)
def test_lint_error(command, exit_code, tmp_empty):
    Path("pyproject.toml").touch()
    Path("tmp_folder1").mkdir()
    Path("tmp_folder2").mkdir()
    Path("tmp_folder1", "file.py").write_text("def stuff():\n\tpass\n\n\n")
    Path("tmp_folder2", "file.py").write_text("a = 1\n")

    runner = CliRunner()
    result = runner.invoke(cli.cli, command.split())

    assert result.exit_code == exit_code

    if exit_code == 1:
        assert "The following command failed: black --check" in result.output
        assert "The following command failed: flake8" in result.output


@pytest.mark.parametrize(
    "command,a,b",
    [
        ["format", "def stuff():\n    pass\n", "a = 1\n"],
        ["format -e tmp_folder1", "def stuff():\n\tpass\n\n\n", "a = 1\n"],
        [
            "format -e tmp_folder1 -e tmp_folder2",
            "def stuff():\n\tpass\n\n\n",
            "a = 1\n\n",
        ],
    ],
)
def test_format_error(command, a, b, tmp_empty, capsys):
    Path("pyproject.toml").touch()
    Path("tmp_folder1").mkdir()
    Path("tmp_folder2").mkdir()
    Path("tmp_folder1", "file.py").write_text("def stuff():\n\tpass\n\n\n")
    Path("tmp_folder2", "file.py").write_text("a = 1\n\n")

    runner = CliRunner()
    result = runner.invoke(cli.cli, command.split(" "))

    assert "Finished formatting with black!" in result.output
    assert Path("tmp_folder1", "file.py").read_text() == a
    assert Path("tmp_folder2", "file.py").read_text() == b


@pytest.mark.parametrize(
    "pyproject,output",
    [
        ["", "a = 1\n"],
        ['[tool.black]\nextend-exclude = "tmp_folder2"', "a = 1\n\n"],
    ],
)
def test_format_black_pyproj(pyproject, output, tmp_empty):
    Path("pyproject.toml").write_text(pyproject)
    Path("tmp_folder1").mkdir()
    Path("tmp_folder2").mkdir()
    Path("tmp_folder1", "file.py").write_text("def stuff():\n\tpass\n\n\n")
    Path("tmp_folder2", "file.py").write_text("a = 1\n\n")

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["format", "-e", "tmp_folder1"])

    assert "Finished formatting with black!" in result.output
    assert Path("tmp_folder1", "file.py").read_text() == "def stuff():\n\tpass\n\n\n"
    assert Path("tmp_folder2", "file.py").read_text() == output


@pytest.mark.parametrize(
    "pyproject,output",
    [
        [
            "",
            "The following command failed: black --check . "
            "--extend-exclude tmp_folder1",
        ],
        ['[tool.black]\nextend-exclude = "tmp_folder2"', ""],
    ],
)
def test_lint_black_pyproj(pyproject, output, tmp_empty):
    Path("pyproject.toml").write_text(pyproject)
    Path("tmp_folder1").mkdir()
    Path("tmp_folder2").mkdir()
    Path("tmp_folder1", "file.py").write_text("def stuff():\n\tpass\n\n\n")
    Path("tmp_folder2", "file.py").write_text("a = 1\n\n")

    runner = CliRunner()
    result = runner.invoke(cli.cli, ["lint", "-e", "tmp_folder1"])

    assert (
        "The following command failed: flake8 . --extend-exclude tmp_folder1"
        in result.output
    )
    assert output in result.output
