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
