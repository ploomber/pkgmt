import subprocess
from pathlib import Path

import pytest

from pkgmt import links

md = """
# Some header

https://docs.ploomber.io

http://docs.ploomber.io

```python
git clone https://github.com/ploomber/ploomber
```

```yaml
repository: gcr.io/PROJECT-ID/my-ploomber-pipeline
```
"""

rst = """
* `Some link <https://docs.ploomber.io>`_
* `Another <http://docs.ploomber.io>`_

.. code-block:: sh

    # clone
    git clone https://github.com/ploomber/ploomber


.. code-block:: yaml

    repository: gcr.io/PROJECT-ID/my-ploomber-pipeline
"""


@pytest.mark.parametrize("text", [md, rst])
def test_find(text):
    assert links._find(text) == [
        "https://docs.ploomber.io",
        "http://docs.ploomber.io",
        "https://github.com/ploomber/ploomber",
        "gcr.io/PROJECT-ID/my-ploomber-pipeline",
    ]


@pytest.mark.parametrize("text", [md, rst])
def test_find_ignore(text):
    assert links._find(text, ignore_substrings=["gcr.io", "docs.ploomber.io"]) == [
        "https://github.com/ploomber/ploomber",
    ]


@pytest.mark.parametrize(
    "url, code, broken",
    [
        ["https://ploomber.io", 200, False],
        ["https://ploomber.io/broken", 404, True],
        ["https://127.0.0.1:2746", None, True],
    ],
)
def test_check_if_broken(url, code, broken):
    response = links._check_if_broken(url)
    assert response.url == url
    assert response.code == code
    assert response.broken == broken


@pytest.mark.parametrize(
    "extensions, expected",
    [
        [
            ("md", "rst"),
            {"https://ploomber.io/broken-another", "https://ploomber.io/broken"},
        ],
        [
            "md",
            {"https://ploomber.io/broken"},
        ],
        [
            "rst",
            {"https://ploomber.io/broken-another"},
        ],
    ],
)
def test_find_broken_in_files(tmp_empty, extensions, expected):
    Path("nested", "dir").mkdir(parents=True)
    Path("file.md").write_text("https://ploomber.io/broken\nhttps://ploomber.io/")
    Path("nested", "dir", "another.rst").write_text(
        "https://ploomber.io/broken-another"
    )

    assert set(links.find_broken_in_files(extensions)) == expected


@pytest.fixture
def sample_files(tmp_empty):
    Path("script.py").write_text(
        """

def function():
    '''
    Notes
    -----
    https://ploomber.io/first
    '''
"""
    )

    dir = Path("some/nested/dir")
    dir.mkdir(parents=True)

    (dir / "another.py").write_text(
        """
def another_function():
    '''
    Notes
    -----
    https://ploomber.io/second
    '''
"""
    )

    Path("doc.md").write_text(
        """
# heading

![img](https://ploomber.io/should-not-appear)
"""
    )


def test_find_links_in_files(sample_files):
    assert links._find_links_in_files(["py"]) == {
        "script.py": ["https://ploomber.io/first"],
        "some/nested/dir/another.py": ["https://ploomber.io/second"],
    }


def test_find_links_in_files_ignores_nontracked_files(sample_files):
    subprocess.check_call(["git", "init"])
    subprocess.check_call(["git", "config", "commit.gpgsign", "false"])
    subprocess.check_call(["git", "config", "user.email", "ci@ploomberio"])
    subprocess.check_call(["git", "config", "user.name", "Ploomber"])
    subprocess.check_call(["git", "add", "script.py"])
    subprocess.check_call(["git", "commit", "-m", "first-commit"])

    assert links._find_links_in_files(["py"]) == {
        "script.py": ["https://ploomber.io/first"],
    }
