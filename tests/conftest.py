import subprocess
import shutil
import os
from pathlib import Path
import tempfile

import pytest

_root = Path(__file__).parent.parent


@pytest.fixture
def root():
    return Path(_root)


@pytest.fixture
def tmp_empty(tmp_path):
    old = os.getcwd()
    os.chdir(str(tmp_path))
    yield str(Path(tmp_path).resolve())
    os.chdir(old)


@pytest.fixture
def tmp_package_name(root, tmp_empty):
    old = os.getcwd()
    path_to_templates = root / "tests" / "assets" / "package_name"
    shutil.copytree(str(path_to_templates), "copy")
    os.chdir("copy")

    subprocess.run(["git", "init"])
    subprocess.check_call(["git", "config", "commit.gpgsign", "false"])
    subprocess.check_call(["git", "config", "user.email", "ci@ploomberio"])
    subprocess.check_call(["git", "config", "user.name", "Ploomber"])
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "some-commit-message"])

    yield tmp_empty

    os.chdir(old)


@pytest.fixture
def tmp_another_package(root, tmp_empty):
    old = os.getcwd()
    path_to_templates = root / "tests" / "assets" / "another_package"
    shutil.copytree(str(path_to_templates), "copy")
    os.chdir("copy")

    subprocess.run(["git", "init"])
    subprocess.check_call(["git", "config", "commit.gpgsign", "false"])
    subprocess.check_call(["git", "config", "user.email", "ci@ploomberio"])
    subprocess.check_call(["git", "config", "user.name", "Ploomber"])
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "some-commit-message"])

    yield tmp_empty

    os.chdir(old)
