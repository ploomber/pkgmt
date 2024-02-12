import subprocess
from pathlib import Path
from unittest.mock import Mock

import requests
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

expected = [
    "https://docs.ploomber.io",
    "http://docs.ploomber.io",
    "https://github.com/ploomber/ploomber",
]

py = """
connect = 'postgresql://user:password@ploomber.io/db',
missing_https = 'ploomber.io/db',
"""

template = """
https://ploomber.io/{something}
"""


@pytest.mark.parametrize(
    "text, expected",
    [(md, expected), (rst, expected), (py, []), (template, [])],
    ids=[
        "md",
        "rst",
        "py",
        "template",
    ],
)
def test_find(text, expected):
    assert links._find(text) == expected


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
    response = links.LinkChecker().check_if_broken(url)
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


def test_find_links_in_files_on_ipynb(tmp_empty, root):
    text = Path(root / "tests" / "assets" / "notebook.ipynb").read_text()
    Path("notebook.ipynb").write_text(text)
    assert links._find_links_in_files(["ipynb"]) == {
        "notebook.ipynb": ["https://ploomber.io"]
    }


def test_find_broken_in_files_only_hits_urls_once(monkeypatch, tmp_empty):
    mock = Mock(wraps=requests.head)
    monkeypatch.setattr(requests, "head", mock)

    Path("doc.md").write_text(
        """
https://ploomber.io

https://ploomber.io

https://ploomber.io
"""
    )

    Path("another.md").write_text(
        """
https://ploomber.io

https://ploomber.io

https://ploomber.io
"""
    )

    links.find_broken_in_files(extensions=["md"])

    mock.assert_called_once_with("https://ploomber.io")


def test_only_consider_404_as_broken(tmp_empty):
    Path("doc.md").write_text(
        """
https://api.ploomber.io

"""
    )

    broken = links.find_broken_in_files(extensions=["md"], broken_http_codes=[404])

    assert not broken


def test_throttles_requests_to_the_same_domain():
    checker = links.LinkChecker()

    checker.check_if_broken("https://ploomber.io/something")
    checker.check_if_broken("https://ploomber.io/another")


def test_verbose_shows_invalid_links(tmp_empty, capsys):
    Path("doc.md").write_text(
        """
https://api.ploomber.io/{something}

https://ploomber.io/something
"""
    )

    links.find_broken_in_files(extensions=["md"], verbose=True)

    captured = capsys.readouterr()
    assert "*** Found invalid links in doc.md ***" in captured.out
