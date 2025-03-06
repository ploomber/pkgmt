import json
from unittest.mock import ANY
from pathlib import Path
import subprocess
import os

from pkgmt import new

import pytest


@pytest.fixture
def uninstall():
    yield
    subprocess.check_call(["pip", "uninstall", "some-cool-pkg", "-y"])


def test_package_setup_py(tmp_empty, uninstall):
    new.package("some-cool_pkg", use_setup_py=True)

    # move the working directory so the settings.py file is found
    os.chdir("some-cool-pkg")
    subprocess.check_call(["pip", "install", "."])

    pyproject = Path("pyproject.toml").read_text()
    setup = Path("setup.py").read_text()
    ci = Path(".github", "workflows", "ci.yml").read_text()
    manifest = Path("MANIFEST.in").read_text()
    init = Path("src", "some_cool_pkg", "__init__.py").read_text()
    cli = Path("src", "some_cool_pkg", "cli.py").read_text()
    assert '__version__ = "0.1dev"\n' in init
    assert 'github = "ploomber/some-cool-pkg"' in pyproject
    assert 'package_name = "some_cool_pkg"' in pyproject
    assert 'env_name = "some-cool-pkg"' in pyproject
    assert 'name="some-cool-pkg"' in setup
    assert "src/some_cool_pkg/__init__.py" in setup
    assert 'python -c "import some_cool_pkg"' in ci
    assert "graft src/some_cool_pkg/assets" in manifest
    assert "# flake8: noqa" not in cli

    subprocess.check_call(["some-cool-pkg", "log", "user"])
    assert json.loads(Path("app.log").read_text()) == {
        "name": "user",
        "event": "Hello, user!",
        "filename": "cli.py",
        "func_name": "log",
        "lineno": ANY,
        "level": "info",
        "timestamp": ANY,
    }


def test_package_pyproject_toml(tmp_empty, uninstall):
    new.package("some-cool_pkg", use_setup_py=False)

    # move the working directory so the settings.py file is found
    os.chdir("some-cool-pkg")
    subprocess.check_call(["pip", "install", "."])

    pyproject = Path("pyproject.toml").read_text()
    ci = Path(".github", "workflows", "ci.yml").read_text()
    init = Path("src", "some_cool_pkg", "__init__.py").read_text()
    cli = Path("src", "some_cool_pkg", "cli.py").read_text()
    assert not Path("setup.py").exists()
    assert not Path("MANIFEST.in").exists()
    assert not Path("pyproject-setup.toml").exists()

    assert "__version__" not in init

    assert 'github = "ploomber/some-cool-pkg"' in pyproject
    assert 'package_name = "some_cool_pkg"' in pyproject
    assert 'env_name = "some-cool-pkg"' in pyproject

    # build settings
    assert 'name = "some-cool-pkg"' in pyproject
    assert (
        'package-data = { "some_cool_pkg" = ["assets/*", "templates/*", "*.md"] }'
        in pyproject
    )

    assert 'python -c "import some_cool_pkg"' in ci
    assert "# flake8: noqa" not in cli

    subprocess.check_call(["some-cool-pkg", "log", "user"])
    assert json.loads(Path("app.log").read_text()) == {
        "name": "user",
        "event": "Hello, user!",
        "level": "info",
        "timestamp": ANY,
    }
