import shutil
import tempfile
import os
import contextlib
from pathlib import Path

import click


def markdown(filename, inplace=True):
    # optional dependencies
    import jupytext
    import nbclient

    front_matter = """\
---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.6
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---
"""

    # add front matter so jupytext correctly identifies the bash cells and adds
    # the %%bash magic
    content = front_matter + Path(filename).read_text()

    nb = jupytext.reads(content)

    click.echo(f"Running {filename}")

    if inplace:
        nbclient.execute(nb)
    else:
        dir_ = Path(tempfile.mkdtemp(), "files")
        click.echo(f"Creating tmp directory: {dir_}")

        click.echo("Copying files to tmp directory...")
        shutil.copytree(".", dir_)

        with chdir(dir_):
            nbclient.execute(nb)

    return nb


@contextlib.contextmanager
def chdir(directory):
    old_dir = os.getcwd()
    try:
        os.chdir(str(directory))
        yield
    finally:
        os.chdir(old_dir)
