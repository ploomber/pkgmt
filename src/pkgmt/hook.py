from pathlib import Path
import stat
import click
import shutil
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

    while not (current / "pyproject.toml").exists():
        if current == current.parent:
            sys.exit("Could not find project root.")

        current = current.parent

    return str(current)


class Runner:
    def __init__(self, cwd) -> None:
        self._cwd = cwd
        self._errors = []

    def run(self, cmd, fix):
        cmd_ = " ".join(cmd)
        header = "=" * 20
        print(f"{header} Running: {cmd_} {header}")
        res = subprocess.run(cmd, cwd=self._cwd)

        if res.returncode:
            self._errors.append((cmd_, fix))

    def check(self):
        if self._errors:
            for cmd, fix in self._errors:
                print(f"The following command failed: {cmd}\\nTo fix it: {fix}")

            return 1
        else:
            print("All checks passed!")
            return 0


def _lint():
    runner = Runner(find_root())
    runner.run(["flake8"], fix="Run: pkgmt format")
    runner.run(["black", "--check", "."], fix="Run: pkgmt format")

    if not nbqa:
        print(
            "nbqa is missing, flake8 won't run on notebooks. "
            "Fix it with: pip install nbqa"
        )

    if not jupytext:
        print(
            "jupytext is missing, flake8 won't run on notebooks. "
            "Fix it with: pip install jupytext"
        )

    if nbqa and jupytext:
        runner.run(
            ["nbqa", "flake8", "."], fix="Install nbqa jupytext and run: pkgmt format"
        )

    return runner.check()


pre_push_hook = """\
#!/usr/bin/env python3
import sys

try:
    from pkgmt.hook import _lint
except ModuleNotFoundError:
    sys.exit("Cannot run pre-push hook. Install pkgmt (pip install pkgmt)")

if _lint():
    sys.exit()
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
