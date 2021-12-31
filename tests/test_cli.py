from pathlib import Path

from click.testing import CliRunner

from pkgmt.cli import cli


def test_check_links(tmp_empty):
    Path('pyproject.toml').write_text("""
[tool.pkgmt.check_links]
extensions = ["md"]
""")

    Path('file.md').write_text('https://ploomber.io/broken')

    runner = CliRunner()
    result = runner.invoke(cli, ['check-links'])
    assert result.exit_code == 1
    assert result.output == '*** file.md ***\nhttps://ploomber.io/broken\n'
