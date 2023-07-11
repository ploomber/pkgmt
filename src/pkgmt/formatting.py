from pathlib import Path
import sys
import subprocess
import click
import toml

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

    if Path("pyproject.toml").exists():
        with open("pyproject.toml") as f:
            data = toml.load(f)

        if "tool" in data and "black" in data["tool"]:
            exclude_pyproj = data["tool"]["black"].get("extend-exclude", "")
        else:
            exclude_pyproj = ""
    else:
        exclude_pyproj = ""

    exclude_str = "|".join(exclude)

    if exclude_pyproj:
        if exclude_str:
            exclude_str += "|" + exclude_pyproj
        else:
            exclude_str = exclude_pyproj

    cmd = ["black", ".", "--extend-exclude", exclude_str]
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
        cmd = ["nbqa", "black", ".", "--extend-exclude", exclude_str]
        click.echo("Running command:" + " ".join(map(quote, cmd)))
        res_nb = subprocess.run(cmd, cwd=current)

        if res_nb.returncode:
            error = True

    if error:
        click.echo()
        sys.exit("***black returned errors.***")

    click.echo("Finished formatting with black!")
