from pathlib import Path
import subprocess
from pkgmt import new

import pytest


@pytest.fixture
def uninstall():
    yield
    subprocess.check_call(["pip", "uninstall", "somepkg", "-y"])


def test_package(tmp_empty, uninstall):
    new.package("somepkg")

    subprocess.check_call(["pip", "install", "somepkg/"])

    pyproject = Path("somepkg", "pyproject.toml").read_text()
    setup = Path("somepkg", "setup.py").read_text()
    ci = Path("somepkg", ".github", "workflows", "ci.yml").read_text()
    manifest = Path("somepkg", "MANIFEST.in").read_text()

    assert 'github = "ploomber/somepkg"' in pyproject
    assert 'package_name = "somepkg"' in pyproject
    assert 'env_name = "somepkg"' in pyproject
    assert 'name="somepkg"' in setup
    assert 'python -c "import somepkg"' in ci
    assert "graft src/somepkg/assets" in manifest
