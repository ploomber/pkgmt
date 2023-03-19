import subprocess
from pathlib import Path
import stat
import click
import shutil
from contextlib import contextmanager


pre_push_hook = """\
#!/usr/bin/env python3

from pathlib import Path
import sys
import subprocess

try:
    import jupytext
except ModuleNotFoundError:
    jupytext = None


try:
    import nbqa
except ModuleNotFoundError:
    nbqa = None


def find_root():
    current = Path().resolve()

    while not (current / 'pyproject.toml').exists():
        if current == current.parent:
            sys.exit('Could not find project root.')

        current = current.parent

    return str(current)


current = find_root()

print("Running: flake8")
res = subprocess.run(['flake8'], cwd=current)

error = False

if res.returncode:
    error = True

if not nbqa:
    print("nbqa is missing, flake8 won't run on notebooks. "
          "Fix it with: pip install nbqa")

if not jupytext:
    print("jupytext is missing, flake8 won't run on notebooks. "
          "Fix it with: pip install jupytext")


if nbqa and jupytext:
    print("Running: nbqa flake8 .")
    res_nb = subprocess.run(["nbqa", "flake8", "."], cwd=current)

    if res_nb.returncode:
        error = True

if error:
    print()
    sys.exit('***flake8 returned errors. Fix and push again.***')

print("flake8 passed!")
"""


def _delete_hook(path):
    """Delete a git hook at the given path"""
    if path.exists():
        if path.is_file():
            path.unlink()
        else:
            # in the remote case that it's a directory
            shutil.rmtree(path)

    click.echo(f"Deleted hook located at {path}")


def _install_hook(path_to_hook, content):
    """
    Install a git hook script at the given path
    """
    if path_to_hook.exists():
        click.echo("Overwriting existing hook...")

    path_to_hook.write_text(content)
    # make the file executable
    path_to_hook.chmod(path_to_hook.stat().st_mode | stat.S_IEXEC)


def install_hook():
    if not Path(".git").is_dir():
        raise NotADirectoryError(
            "Expected a .git/ directory in the current working "
            "directory. Run this from the repository root directory."
        )

    parent = Path(".git", "hooks")
    parent.mkdir(exist_ok=True)

    _install_hook(parent / "pre-push", pre_push_hook)
    click.echo("Successfully installed pre-push git hook")


def uninstall_hook():
    _delete_hook(Path(".git", "hooks", "pre-push"))


def run_hook():
    """Run hook without installing it"""
    with tmp_file() as path:
        path.write_text(pre_push_hook)
        return subprocess.run(["python", "_pkgmt_hook.py"]).returncode


@contextmanager
def tmp_file():
    path = Path("_pkgmt_hook.py")

    try:
        yield path
    finally:
        if path.exists():
            path.unlink()
