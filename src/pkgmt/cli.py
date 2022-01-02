from pathlib import Path
import sys

import click

from pkgmt import links
from pkgmt import config


@click.group()
def cli():
    pass


@cli.command()
def check_links():
    """Check for broken links
    """
    cfg = config.load()['check_links']
    out = links.find_broken_in_files(cfg['extensions'],
                                     cfg.get('ignore_substrings'),
                                     verbose=True)

    if out:
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(exists=True, dir_okay=False))
@click.option('-o', '--output', default=None, type=click.Path(exists=False))
def execute(path, output):
    """Execute rst files
    """
    from pkgmt.testing import rst
    code = rst.parse_from_path(path)

    if output:
        click.echo(f'Writing script to {output}')
        Path(output).write_text(code)
    else:
        click.echo(code)
