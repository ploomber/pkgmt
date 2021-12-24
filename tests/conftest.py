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
