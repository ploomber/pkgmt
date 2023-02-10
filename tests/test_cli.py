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
def test_version(backup_package_name, monkeypatch, args, yes, push, tag, target):
    mock = Mock()

    monkeypatch.setattr(cli.versioneer, "version", mock)

    runner = CliRunner()
    runner.invoke(cli.cli, args)

    mock.assert_called_once_with(
        project_root=".", tag=tag, yes=yes, push=push, target=target
    )
