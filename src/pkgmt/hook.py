from pathlib import Path
import stat
import click
import shutil


pre_push_hook = """\
#!/usr/bin/env python3

from pathlib import Path
import sys
import subprocess

def find_root():
    current = Path().resolve()

    while not (current / 'pyproject.toml').exists():
        if current == current.parent:
            sys.exit('Could not find project root.')

        current = current.parent

    return str(current)

current = find_root()

print(f'Running flake8 from {current!r}')
res = subprocess.run(['flake8'])

if res.returncode:
    print()
    sys.exit('***flake8 returned errors. Fix and push again.***')
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
