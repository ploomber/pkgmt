import subprocess
from pkgmt import new

import pytest


@pytest.fixture
def uninstall():
    yield
    subprocess.check_call(['pip', 'uninstall', 'somepkg', '-y'])


def test_package(tmp_empty, uninstall):
    new.package('somepkg')

    subprocess.check_call(['pip', 'install', 'somepkg/'])
