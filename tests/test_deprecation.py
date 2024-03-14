from pathlib import Path

import pytest

from pkgmt import deprecation
from pkgmt.exceptions import ProjectValidationError


@pytest.mark.parametrize(
    "text, body, version",
    [
        [
            '''
def function():
    """
    Notes
    -----
    .. deprecated:: 1.2.3

        -Attention, `module.function` removed in 1.3
    """
    pass
''',
            ["-Attention, `module.function` removed in 1.3\n"],
            ["1.3"],
        ],
        [
            '''
def function():
    """
    Notes
    -----
    .. deprecated:: 1.2.3
        Stuff removed in 1.3, -update `module.function`
    """
    pass
''',
            ["Stuff removed in 1.3, -update `module.function`\n"],
            ["1.3"],
        ],
        [
            '''
def function():
    """
    Notes
    -----
    .. deprecated:: 1.2.3
        This
        description spans
        multiple lines. Removed in 1.3.4
        so update
    """
    pass
''',
            (
                [
                    "This\n        description spans\n        "
                    "multiple lines. Removed in 1.3.4\n        so update\n"
                ]
            ),
            ["1.3.4"],
        ],
        [
            '''
def function():
    """
    Notes
    -----
    .. deprecated:: 1.2.3
        Will be removed in 1.3
    """
    pass

def another():
    """
    Notes
    -----
    .. deprecated:: 1.2.6
        Will be removed in 1.4
    """
    pass
''',
            ["Will be removed in 1.3\n", "Will be removed in 1.4\n"],
            ["1.3", "1.4"],
        ],
    ],
    ids=[
        "simple",
        "trailing-text",
        "multi-line-directive",
        "multiple",
    ],
)
def test_find_deprecations_in_text(text, body, version):
    body_returned, version_returned = deprecation._find_deprecations_in_text(text)
    assert body_returned == body
    assert version_returned == version


def test_find_deprecations(tmp_empty):
    Path("some/nested/dir").mkdir(parents=True)

    Path("some/nested/dir/functions.py").write_text(
        '''

def stuff():
    """
    Notes
    -----
    .. deprecated:: 0.5.6
        Removed in 0.6
    """
    pass

def more_stuff():
    """
    Notes
    -----
    .. deprecated:: 0.5.6
        Removed in 0.6.0
    """
    pass
'''
    )

    Path("some/nested/functions.py").write_text(
        '''

def stuff():
    """
    Notes
    -----
    .. deprecated:: 0.1
        Removed in 0.2
    """
    pass
'''
    )

    Path("functions.py").write_text(
        '''

def stuff():
    """
    Notes
    -----
    .. deprecated:: 0.9
        Removed in 0.9.0
    """
    pass
'''
    )

    expected = {
        deprecation.DeprecationItem(
            "Removed in 0.6\n", "0.6", "some/nested/dir/functions.py"
        ),
        deprecation.DeprecationItem(
            "Removed in 0.6.0\n", "0.6.0", "some/nested/dir/functions.py"
        ),
        deprecation.DeprecationItem(
            "Removed in 0.2\n", "0.2", "some/nested/functions.py"
        ),
        deprecation.DeprecationItem("Removed in 0.9.0\n", "0.9.0", "functions.py"),
    }

    assert set(deprecation.find_deprecations(root_dir=".")) == expected


def test_check(tmp_package_name):
    Path("src", "package_name", "__init__.py").write_text(
        """
__version__ = "0.9dev"
"""
    )

    Path("src/package_name/functions.py").write_text(
        '''

def stuff():
    """
    Notes
    -----
    .. deprecated:: 0.8.1
        Removed in 0.9.0
    """
    pass


def more_stuff():
    """
    Notes
    -----
    .. deprecated:: 0.8.2
        Also removed in 0.9
    """
    pass
'''
    )

    dep = deprecation.Deprecations()

    with pytest.raises(ProjectValidationError) as excinfo:
        dep.check()

    assert "Found the following pending deprecations" in str(excinfo.value)
    assert "Removed in 0.9.0" in str(excinfo.value)
    assert "Also removed in 0.9" in str(excinfo.value)
