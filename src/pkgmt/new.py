import os
from pathlib import Path
import shutil
import importlib.resources
from string import Template

from pkgmt import assets


def render_inplace(path, **kwargs):
    template = Template(path.read_text())
    path.write_text(template.safe_substitute(**kwargs))


def package(name):
    """Create a new package
    """
    # .path doesn't work with directories
    with importlib.resources.path(assets, '__init__.py') as p:
        # so we trick it
        path = p.parent / 'template'

    shutil.copytree(path, name)

    root = Path(name)

    for file in ('README.md', 'setup.py', 'tasks.py', 'MANIFEST.in'):
        render_inplace(root / file, name=name)

    os.rename(root / 'src' / 'name', root / 'src' / name)
