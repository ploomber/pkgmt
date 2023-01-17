import sys
from pathlib import Path

import click

from pkgmt import links, config, test, changelog, hook as hook_, versioneer
from pkgmt import new as new_


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--only-404",
    is_flag=True,
    default=False,
    help="Only consider 404 code as broken",
)
def check_links(only_404):
    """Check for broken links"""
    broken_http_codes = None if not only_404 else [404]

    cfg = config.load()["check_links"]
    out = links.find_broken_in_files(
        cfg["extensions"],
        cfg.get("ignore_substrings"),
        verbose=True,
        broken_http_codes=broken_http_codes,
    )

    if out:
        sys.exit(1)


@cli.command()
@click.argument("name")
def new(name):
    """Create new package"""
    new_.package(name)


@cli.command()
@click.option(
    "-f", "--file", type=click.Path(dir_okay=False, exists=True), default="README.md"
)
@click.option("-i", "--inplace", is_flag=True, show_default=True, default=False)
def test_md(file, inplace):
    """Run a markdown file"""
    test.markdown(file, inplace=inplace)


@cli.command()
def check():
    """Run general checks in the project"""
    text = Path("CHANGELOG.md").read_text()
    changelog.CHANGELOG(text).check(verbose=True)


@cli.command()
@click.option(
    "--uninstall",
    is_flag=True,
    default=False,
    help="Uninstall hook",
)
def hook(uninstall):
    """Install pre-push hook"""

    if uninstall:
        hook_.uninstall_hook()
        click.echo("hook uninstalled.")
    else:
        hook_.install_hook()


@cli.command()
@click.option(
    "--yes",
    is_flag=True,
    default=False,
    help="Do not ask for confirmation",
)
def version(yes):
    """Create a new package version"""
    versioneer.version(project_root=".", tag=True, yes=yes)


@cli.command()
@click.argument("tag")
@click.option(
    "--production",
    is_flag=True,
    default=False,
    help="Upload to the production PyPI server",
)
def release(tag, production):
    """Release this package from a given tag"""
    versioneer.upload(tag, production)
