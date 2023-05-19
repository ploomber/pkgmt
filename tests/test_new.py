from pathlib import Path
import subprocess
from pkgmt import new

import pytest


@pytest.fixture
def uninstall():
    yield
    subprocess.check_call(["pip", "uninstall", "somepkg", "-y"])


def test_package(tmp_empty, uninstall):
    new.package("some-cool_pkg")

    subprocess.check_call(["pip", "install", "some-cool-pkg/"])

    pyproject = Path("some-cool-pkg", "pyproject.toml").read_text()
    setup = Path("some-cool-pkg", "setup.py").read_text()
    ci = Path("some-cool-pkg", ".github", "workflows", "ci.yml").read_text()
    manifest = Path("some-cool-pkg", "MANIFEST.in").read_text()

    assert 'github = "ploomber/some-cool-pkg"' in pyproject
    assert 'package_name = "some_cool_pkg"' in pyproject
    assert 'env_name = "some-cool-pkg"' in pyproject
    assert 'name="some-cool-pkg"' in setup
    assert "src/some_cool_pkg/__init__.py" in setup
    assert 'python -c "import some_cool_pkg"' in ci
    assert "graft src/some_cool_pkg/assets" in manifest
