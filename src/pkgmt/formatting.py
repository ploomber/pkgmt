from pathlib import Path
import sys
import subprocess
import click

try:
    import jupytext
except ModuleNotFoundError:
    jupytext = None


try:
    import nbqa
except ModuleNotFoundError:
    nbqa = None
from shlex import quote


def find_root():
    current = Path().resolve()

    while not (current / "pyproject.toml").exists():
        if current == current.parent:
            sys.exit(
                (
                    "Could not find project root."
                    "Please add a pyproject.toml file in the root folder."
                )
            )

        current = current.parent

    return str(current)


def format(exclude):
    current = find_root()

    exclude_str = "|".join(exclude)

    if exclude_str:
        cmd = ["black", ".", "--extend-exclude", exclude_str]
    else:
        cmd = ["black", "."]
    click.echo("Running command:" + " ".join(map(quote, cmd)))
    res = subprocess.run(cmd, cwd=current)

    error = False

    if res.returncode:
        error = True

    if not nbqa:
        click.echo(
            "nbqa is missing, black won't run on notebooks. "
            "Fix it with: pip install nbqa"
        )

    if not jupytext:
        click.echo(
            "jupytext is missing, black won't run on notebooks. "
            "Fix it with: pip install jupytext"
        )

    if nbqa and jupytext:
        if exclude_str:
            cmd = ["nbqa", "black", ".", "--extend-exclude", exclude_str]
        else:
            cmd = [
                "nbqa",
                "black",
                ".",
            ]
        click.echo("Running command:" + " ".join(map(quote, cmd)))
        res_nb = subprocess.run(cmd, cwd=current)

        if res_nb.returncode:
            error = True

    if error:
        click.echo()
        sys.exit("***black returned errors.***")

    click.echo("Finished formatting with black!")
