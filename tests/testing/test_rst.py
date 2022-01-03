from pkgmt.testing import rst

import pytest

empty_in = ''
empty_out = '# exit on error and print each command\nset -e\nset -x\n\n'

simple_in = """\

Some text

.. code-block:: bash

    echo hi

.. code-block:: sh

    echo bye
"""

simple_out = """\
# exit on error and print each command
set -e
set -x

echo hi

echo bye\
"""

skip_in = """\

Some text

.. code-block:: bash

    echo hi

.. skip-next
.. code-block:: sh

    echo ignore
"""

skip_out = """\
# exit on error and print each command
set -e
set -x

echo hi\
"""


@pytest.mark.parametrize('in_, out', [
    [empty_in, empty_out],
    [simple_in, simple_out],
    [skip_in, skip_out],
])
def test_to_script(in_, out):
    assert rst.to_script(in_) == out
