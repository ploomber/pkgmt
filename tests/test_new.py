from pathlib import Path
import subprocess
from pkgmt import new

import pytest


@pytest.fixture
def uninstall():
    yield
    subprocess.check_call(["pip", "uninstall", "somepkg", "-y"])


def test_package_setup_py(tmp_empty, uninstall):
    new.package("some-cool_pkg", use_setup_py=True)

    subprocess.check_call(["pip", "install", "some-cool-pkg/"])

    pyproject = Path("some-cool-pkg", "pyproject.toml").read_text()
    setup = Path("some-cool-pkg", "setup.py").read_text()
    ci = Path("some-cool-pkg", ".github", "workflows", "ci.yml").read_text()
    manifest = Path("some-cool-pkg", "MANIFEST.in").read_text()
    init = Path("some-cool-pkg", "src", "some_cool_pkg", "__init__.py").read_text()

    assert '__version__ = "0.1dev"\n' == init
    assert 'github = "ploomber/some-cool-pkg"' in pyproject
    assert 'package_name = "some_cool_pkg"' in pyproject
    assert 'env_name = "some-cool-pkg"' in pyproject
    assert 'name="some-cool-pkg"' in setup
    assert "src/some_cool_pkg/__init__.py" in setup
    assert 'python -c "import some_cool_pkg"' in ci
    assert "graft src/some_cool_pkg/assets" in manifest


def test_package_pyproject_toml(tmp_empty, uninstall):
    new.package("some-cool_pkg", use_setup_py=False)

    subprocess.check_call(["pip", "install", "some-cool-pkg/"])

    pyproject = Path("some-cool-pkg", "pyproject.toml").read_text()
    ci = Path("some-cool-pkg", ".github", "workflows", "ci.yml").read_text()
    init = Path("some-cool-pkg", "src", "some_cool_pkg", "__init__.py").read_text()

    assert not Path("some-cool-pkg", "setup.py").exists()
    assert not Path("some-cool-pkg", "MANIFEST.in").exists()
    assert not Path("some-cool-pkg", "pyproject-setup.toml").exists()

    assert init == ""

    assert 'github = "ploomber/some-cool-pkg"' in pyproject
    assert 'package_name = "some_cool_pkg"' in pyproject
    assert 'env_name = "some-cool-pkg"' in pyproject

    # build settings
    assert 'name = "some-cool-pkg"' in pyproject
    assert 'package-data = { "some_cool_pkg" = ["assets/*", "*.md"] }' in pyproject

    assert 'python -c "import some_cool_pkg"' in ci
