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
    """Create a new package"""
    project_name = name.replace("_", "-")
    package_name = name.replace("-", "_")

    # .path doesn't work with directories
    with importlib.resources.path(assets, "__init__.py") as p:
        # so we trick it
        path = p.parent / "template"

    shutil.copytree(path, project_name)

    root = Path(project_name)

    for file in (
        "README.md",
        "setup.py",
        "tasks.py",
        "MANIFEST.in",
        "pyproject.toml",
        ".github/workflows/ci.yml",
    ):
        render_inplace(
            root / file,
            project_name=project_name,
            package_name=package_name,
        )

    os.rename(root / "src" / "package_name", root / "src" / package_name)
