import os
from pathlib import Path
import shutil
import importlib.resources
from string import Template
import re
from pkgmt import assets


def render_inplace(path, **kwargs):
    template = Template(path.read_text())
    path.write_text(template.safe_substitute(**kwargs))


def package(name, use_setup_py=False):
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
        "pyproject-setup.toml",
        ".github/workflows/ci.yml",
        "src/package_name/cli.py",
        "src/package_name/log.py",
        "src/package_name/__init__.py",
    ):
        render_inplace(
            root / file,
            project_name=project_name,
            package_name=package_name,
        )

    os.rename(root / "src" / "package_name", root / "src" / package_name)

    if use_setup_py:
        (root / "pyproject-setup.toml").unlink()
    else:
        (root / "pyproject.toml").unlink()
        (root / "setup.py").unlink()
        (root / "MANIFEST.in").unlink()
        (root / "pyproject-setup.toml").rename(root / "pyproject.toml")

        # Remove __version__ from __init__.py
        content = (root / "src" / package_name / "__init__.py").read_text()
        lines = content.splitlines()
        new_lines = [
            line for line in lines if not re.match(r"__version__\s+=\s+", line)
        ]
        (root / "src" / package_name / "__init__.py").write_text("\n".join(new_lines))

    # Remove flake8: noqa comments from Python files, we added them because
    # they contain $TAG, which raises a warning when linting
    for py_file in root.rglob("*.py"):
        content = py_file.read_text()
        lines = content.splitlines()

        # Process each line
        new_lines = []
        for line in lines:
            # Skip lines that only contain the noqa comment
            if line.strip() == "# flake8: noqa":
                continue
            # Remove the noqa substring from other lines
            if "# flake8: noqa" in line:
                line = line.replace("# flake8: noqa", "").rstrip()
            new_lines.append(line)

        # Write back the cleaned content
        py_file.write_text("\n".join(new_lines) + "\n")
