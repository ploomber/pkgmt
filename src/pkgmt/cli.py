import sys

import click

from pkgmt import links, config, test
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
