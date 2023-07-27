import sys
from pathlib import Path

import click
from invoke import Context, UnexpectedExit


from pkgmt import links, config, test, changelog, hook as hook_, versioneer
from pkgmt import new as new_
from pkgmt import dev
from pkgmt import formatting


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

    cfg = config.Config.from_file("pyproject.toml")["check_links"]
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
@click.option(
    "--run",
    is_flag=True,
    default=False,
    help="Run hook without installing it",
)
def hook(uninstall, run):
    """Install pre-push hook"""

    if run:
        hook_._lint()
    elif uninstall:
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
@click.option("--push/--no-push", default=None)
@click.option("--tag/--no-tag", default=None)
@click.option("--target", default=None)
def version(yes, push, tag, target):
    """Create a new package version"""

    cfg = config.Config.from_file("pyproject.toml", cli_args=dict(push=push, tag=tag))

    versioneer.version(
        project_root=".",
        tag=cfg["version"]["tag"],
        yes=yes,
        push=cfg["version"]["push"],
        target=target,
    )


@cli.command()
@click.argument("tag")
@click.option(
    "--production",
    is_flag=True,
    default=False,
    help="Upload to the production PyPI server",
)
@click.option(
    "--yes",
    is_flag=True,
    default=False,
    help="Do not ask for confirmation",
)
def release(tag, production, yes):
    """Release this package from a given tag"""
    versioneer.upload(tag, production, yes=yes)


@cli.command()
@click.option(
    "--doc",
    is_flag=True,
    default=False,
    help="Install documentation dependencies",
)
def setup(doc):
    """Setup development environment

    Create conda environment and install dependencies:

        $ pkgmt setup

    Install dependencies required to build documentation:

        $ pkgmt setup --doc
    """
    try:
        dev.setup(Context(), doc=doc)
    except UnexpectedExit as e:
        raise SystemExit(f"Error running: {e.result.command}") from e


@cli.command()
@click.option(
    "--clean",
    is_flag=True,
    default=False,
    help="Perform a clean build",
)
def doc(clean):
    """Build docs"""
    try:
        dev.doc(Context(), clean=clean)
    except UnexpectedExit as e:
        raise SystemExit(f"Error running: {e.result.command}") from e


@cli.command()
@click.option(
    "-e",
    "--exclude",
    multiple=True,
    default=[],
    help="Exclude multiple files or dir from the build. Can also pass regex."
    "Eg: -e tmp -e tmp/a.py -e tmp|src",
)
def format(exclude):
    """Run black on .py files and notebooks (.ipynb, .md)"""
    formatting.format(exclude)


@cli.command()
@click.argument("files", nargs=-1)
@click.option(
    "-e",
    "--exclude",
    multiple=True,
    default=[],
    help="Exclude multiple files or dir from the build" "Eg: -e tmp -e tmp/a.py",
)
def lint(files, exclude):
    """Lint .py files and notebooks (.ipynb, .md) with flake8"""
    returncode = hook_._lint(files=files, exclude=exclude)

    if returncode:
        raise SystemExit("Error linting")
