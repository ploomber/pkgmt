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

    while not (current / "pyproject.toml").exists():
        if current == current.parent:
            sys.exit("Could not find project root.")

        current = current.parent

    return str(current)


def format():
    current = find_root()

    print("Running: black .")
    res = subprocess.run(["black", "."], cwd=current)

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
        print("Running: nbqa black .")
        res_nb = subprocess.run(["nbqa", "black", "."], cwd=current)

        if res_nb.returncode:
            error = True

    if error:
        print()
        sys.exit("***black returned errors.***")

    print("Finished formatting with black!")
