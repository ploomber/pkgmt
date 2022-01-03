from pathlib import Path

import pytest

from pkgmt.testing import docker

simple_in = """\

Some text

.. code-block:: bash

    git clone some-repository
    cd some-repository

.. code-block:: bash

    docker run -i -t some-image /bin/bash

.. code-block:: sh

    echo 'hello from docker'

"""

simple_test = """\
# exit on error and print each command
set -e
set -x
ROOT=$(pwd)

git clone some-repository
cd some-repository

cd $ROOT && cat run-in-docker.sh | docker run -i some-image /bin/bash\
"""

simple_run_in_docker = """\
# exit on error and print each command
set -e
set -x
ROOT=$(pwd)

echo 'hello from docker'\
"""

multicommand_in = """\

.. code-block:: bash

    git clone some-repository
    cd some-repository

.. code-block:: bash

    echo hello
    docker run -i -t some-image /bin/bash

.. code-block:: sh

    echo 'hello from docker'

"""

multicommand_test = """\
# exit on error and print each command
set -e
set -x
ROOT=$(pwd)

git clone some-repository
cd some-repository

echo hello
cd $ROOT && cat run-in-docker.sh | docker run -i some-image /bin/bash\
"""

multicommand_run_in_docker = """\
# exit on error and print each command
set -e
set -x
ROOT=$(pwd)

echo 'hello from docker'\
"""


def test_to_script():
    pre, post = docker.to_script(simple_in)
    assert pre == [
        'git clone some-repository\ncd some-repository',
        'docker run -i -t some-image /bin/bash',
    ]
    assert post == ["echo 'hello from docker'"]


@pytest.mark.parametrize('in_, test, run_in_docker', [
    [simple_in, simple_test, simple_run_in_docker],
    [multicommand_in, multicommand_test, multicommand_run_in_docker],
])
def test_to_testing_files(tmp_empty, in_, test, run_in_docker):
    docker.to_testing_files(in_)

    test_out = Path('test.sh').read_text()
    run_in_docker_out = Path('run-in-docker.sh').read_text()

    assert test_out == test
    assert run_in_docker_out == run_in_docker
