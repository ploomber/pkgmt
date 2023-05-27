"""
Tools to help contributors develop locally
"""
import platform
import os
import shutil
from pathlib import Path

from invoke import task
from pkgmt.config import load

community = "https://ploomber.io/community"


class CommandError(SystemExit):
    def __init__(self, msg) -> None:
        super().__init__(
            f"Error: {msg}\nIf you need help, send us a message: {community}"
        )


def _check():
    if not Path("setup.py").exists():
        raise CommandError(
            "Run the command from the root folder (the directory "
            "with the README.md and setup.py files)"
        )

    if Path("tasks.py").exists():
        raise CommandError(
            "This project contains a tasks.py file, use invoke to run commands:\n"
            "$ pip install invoke\n$ invoke --list"
        )


def _update_env(c, conda_hook, env_name, path_to_file):
    c.run(
        f"{conda_hook} "
        f"&& conda activate {env_name} "
        f"&& conda env update --file {path_to_file} --name {env_name}"
    )


def _extras2filename(extras):
    return f"environment.{extras}.yml"


@task()
def setup(c, version=None, doc=False, extras=None):
    """
    Setup dev environment, requires conda
    """
    extras = extras or []

    _check()

    if not shutil.which("conda"):
        raise CommandError("conda not installed. Install it an try again.")

    cfg = load()

    env_prefix = cfg.get("env_name", cfg["package_name"])
    pkg_name = cfg["package_name"]

    version = version or "3.10"
    suffix = "" if version == "3.10" else version.replace(".", "")
    env_name = f"{env_prefix}{suffix}"

    # check the current env doesn't have the same name that the one we'll create
    if os.environ.get("CONDA_DEFAULT_ENV") == env_name:
        raise CommandError(
            f"This command will create an environment named {env_name!r} "
            "but your current environment has the same name. Switch "
            "to another environment, install pkgmt and try again. Example:\n"
            "$ conda create --name tmp python=3.10\n"
            "$ conda activate tmp\n"
            "$ pip install pkmgt\n"
            "$ pkgmt setup\n"
        )

    c.run(f"conda create --name {env_name} python={version} --yes")

    if platform.system() == "Windows":
        conda_hook = "conda shell.bash hook "
    else:
        conda_hook = 'eval "$(conda shell.bash hook)" '

    c.run(f"{conda_hook} && conda activate {env_name} && pip install --editable .[dev]")

    if doc:
        c.run(
            f"{conda_hook} "
            f"&& conda activate {env_name} "
            f"&& conda env update --file doc/environment.yml --name {env_name}"
        )

    for e in extras:
        # skip if extras file does not exist
        _update_env(c, conda_hook, env_name, _extras2filename(e))

    r = c.run(
        f"{conda_hook} && conda activate {env_name} && "
        # fix for windows: https://github.com/ploomber/pkgmt/pull/36
        f'python -c "import {pkg_name}; print({pkg_name})"'
    )

    if "site-packages" in r.stdout:
        raise ValueError(f"Error! {r.stdout}")

    print(f"Package name: {pkg_name}")
    print(f"Done! Activate your environment with:\nconda activate {env_name}")


@task()
def doc(c, clean):
    _check()

    if clean:
        path_to_build = Path("doc", "_build")

        if path_to_build.exists():
            shutil.rmtree(str(path_to_build))

    if Path("doc", "conf.py").exists():
        with c.cd("doc"):
            c.run(
                "python3 -m sphinx -T -E -W --keep-going -b html "
                "-d _build/doctrees -D language=en . _build/html"
            )
    elif Path("doc", "_config.yml").exists():
        c.run("jupyter-book build doc/ --warningiserror --keep-going")
    else:
        raise CommandError(
            "This command only works for projects with a doc/conf.py "
            "or a doc/_config.yml file"
        )

    print("Done! Documentation is located in doc/_build/html/index.html")
