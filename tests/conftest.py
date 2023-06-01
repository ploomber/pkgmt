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
    old = os.getcwd()
    path_to_templates = root / "tests" / "assets" / "package_name"
    shutil.copytree(str(path_to_templates), "copy")
    os.chdir("copy")

    subprocess.run(["git", "init"])
    subprocess.check_call(["git", "config", "commit.gpgsign", "false"])
    subprocess.check_call(["git", "config", "user.email", "ci@ploomberio"])
    subprocess.check_call(["git", "config", "user.name", "Ploomber"])
    subprocess.run(["git", "checkout", "-b", "main"])
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "init-commit-message"])

    subprocess.run(["git", "checkout", "-b", "test_modified_doc"])
    subprocess.run(["mkdir", "-p", "test_doc1"])
    subprocess.run(["touch", "test_doc1/test_modified.txt"])
    subprocess.run(["mkdir", "-p", "test_doc2"])
    subprocess.run(["touch", "test_doc2/test_modified.txt"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "test_modified"])

    yield tmp_empty

    os.chdir(old)


@pytest.fixture
def tmp_package_modi_2(root, tmp_empty):
    old = os.getcwd()
    path_to_templates = root / "tests" / "assets" / "package_name"
    shutil.copytree(str(path_to_templates), "copy")
    os.chdir("copy")

    subprocess.run(["git", "init"])
    subprocess.check_call(["git", "config", "commit.gpgsign", "false"])
    subprocess.check_call(["git", "config", "user.email", "ci@ploomberio"])
    subprocess.check_call(["git", "config", "user.name", "Ploomber"])
    subprocess.run(["git", "checkout", "-b", "main"])
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "init-commit-message"])

    # main branch: create doc/file.txt, commit
    subprocess.run(["mkdir", "-p", "doc"])
    subprocess.run(["touch", "doc/file.txt"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "added doc/file.txt"])

    # checkout to test branch, create doc/another.txt, commit
    subprocess.run(["git", "checkout", "-b", "test_modified_doc"])
    subprocess.run(["mkdir", "-p", "doc"])
    subprocess.run(["touch", "doc/another.txt"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "add doc/another.txt"])

    # checkout main again, create something/file.txt, commit
    subprocess.run(["git", "checkout", "main"])
    subprocess.run(["mkdir", "-p", "something"])
    subprocess.run(["touch", "something/file.txt"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "added something/file.txt"])

    yield tmp_empty

    os.chdir(old)
