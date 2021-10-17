from pathlib import Path

import pytest

_root = Path(__file__).parent.parent


@pytest.fixture
def root():
    return Path(_root)
