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
    if len(exclude) != 1:
        exclude_str = f"/{exclude_str}/"

    cmd = ["black", ".", f"--extend-exclude={exclude_str}"]
    print("Running command:", " ".join(map(quote, cmd)))
    res = subprocess.run(cmd, cwd=current)

    error = False

    if res.returncode:
        error = True

    if not nbqa:
        print(
            "nbqa is missing, black won't run on notebooks. "
            "Fix it with: pip install nbqa"
        )

    if not jupytext:
        print(
            "jupytext is missing, black won't run on notebooks. "
            "Fix it with: pip install jupytext"
        )

    if nbqa and jupytext:
        cmd = ["nbqa", "black", ".", f"--extend-exclude={exclude_str}"]
        print("Running command:", " ".join(map(quote, cmd)))
        res_nb = subprocess.run(cmd, cwd=current)

        if res_nb.returncode:
            error = True

    if error:
        print()
        sys.exit("***black returned errors.***")

    print("Finished formatting with black!")
