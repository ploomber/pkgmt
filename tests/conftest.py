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
def backup_package_name(root):
    old = os.getcwd()
    backup = tempfile.mkdtemp()
    backup_package_name = str(Path(backup, "backup-template"))
    path_to_templates = root / "tests" / "assets" / "package_name"
    shutil.copytree(str(path_to_templates), backup_package_name)

    os.chdir(path_to_templates)

    yield path_to_templates

    os.chdir(old)

    shutil.rmtree(str(path_to_templates))
    shutil.copytree(backup_package_name, str(path_to_templates))
    shutil.rmtree(backup)
