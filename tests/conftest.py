import subprocess
import shutil
import os
from pathlib import Path

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


@pytest.fixture
def tmp_package_modi(root, tmp_empty):
    old = Path.cwd()
    path_to_templates = root / "tests" / "assets" / "package_name"
    shutil.copytree(str(path_to_templates), "copy")
    Path.cwd().joinpath("copy")

    subprocess.run(["git", "init"])
    subprocess.check_call(["git", "config", "commit.gpgsign", "false"])
    subprocess.check_call(["git", "config", "user.email", "ci@ploomberio"])
    subprocess.check_call(["git", "config", "user.name", "Ploomber"])
    subprocess.run(["git", "checkout", "-b", "main"])
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "init-commit-message"])

    subprocess.run(["git", "checkout", "-b", "test_modified_doc"])
    Path("test_doc1").mkdir(parents=True, exist_ok=True)
    Path("test_doc1/test_modified.txt").touch()
    Path("test_doc2").mkdir(parents=True, exist_ok=True)
    Path("test_doc2/test_modified.txt").touch()
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "test_modified"])

    yield tmp_empty

    Path.cwd().joinpath(old)


@pytest.fixture
def tmp_package_modi_2(root, tmp_empty):
    old = Path.cwd()
    path_to_templates = root / "tests" / "assets" / "package_name"
    shutil.copytree(str(path_to_templates), "copy")
    Path.cwd().joinpath("copy")

    subprocess.run(["git", "init"])
    subprocess.check_call(["git", "config", "commit.gpgsign", "false"])
    subprocess.check_call(["git", "config", "user.email", "ci@ploomberio"])
    subprocess.check_call(["git", "config", "user.name", "Ploomber"])
    subprocess.run(["git", "checkout", "-b", "main"])
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "init-commit-message"])

    Path.cwd().joinpath("doc").mkdir(parents=True, exist_ok=True)
    Path.cwd().joinpath("doc", "file.txt").touch()
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "added doc/file.txt"])

    subprocess.run(["git", "checkout", "-b", "test_modified_doc"])
    Path.cwd().joinpath("doc").mkdir(parents=True, exist_ok=True)
    Path.cwd().joinpath("doc", "another.txt").touch()
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "add doc/another.txt"])

    subprocess.run(["git", "checkout", "main"])
    Path.cwd().joinpath("something").mkdir(parents=True, exist_ok=True)
    Path.cwd().joinpath("something", "file.txt").touch()
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "added something/file.txt"])

    yield tmp_empty

    Path.cwd().joinpath(old)
