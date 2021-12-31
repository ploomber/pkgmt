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


@pytest.mark.parametrize('text', [md, rst])
def test_find(text):
    assert links._find(text) == [
        'https://docs.ploomber.io',
        'http://docs.ploomber.io',
        'https://github.com/ploomber/ploomber',
        'gcr.io/PROJECT-ID/my-ploomber-pipeline',
    ]


@pytest.mark.parametrize('text', [md, rst])
def test_find_ignore(text):
    assert links._find(text,
                       ignore_substrings=['gcr.io', 'docs.ploomber.io']) == [
                           'https://github.com/ploomber/ploomber',
                       ]


@pytest.mark.parametrize('url, code, broken', [
    ['https://ploomber.io', 200, False],
    ['https://ploomber.io/broken', 404, True],
    ['https://127.0.0.1:2746', None, True],
])
def test_check_if_broken(url, code, broken):
    response = links._check_if_broken(url)
    assert response.url == url
    assert response.code == code
    assert response.broken == broken


def test_find_broken_in_text():
    text = """
https://ploomber.io

https://ploomber.io/broken

https://github.com/ploomber/ploomber

https://github.com/ploomber/unknown-repo

https://127.0.0.1:2746
"""
    assert links.find_broken_in_text(text) == [
        'https://ploomber.io/broken',
        'https://github.com/ploomber/unknown-repo',
        'https://127.0.0.1:2746',
    ]


@pytest.mark.parametrize('extensions, expected', [
    [
        ('md', 'rst'),
        {
            'file.md': ['https://ploomber.io/broken'],
            'nested/dir/another.rst': ['https://ploomber.io/broken-another']
        },
    ],
    [
        'md',
        {
            'file.md': ['https://ploomber.io/broken']
        },
    ],
    [
        'rst',
        {
            'nested/dir/another.rst': ['https://ploomber.io/broken-another']
        },
    ],
])
def test_find_broken_in_files(tmp_empty, extensions, expected):
    Path('nested', 'dir').mkdir(parents=True)
    Path('file.md').write_text(
        'https://ploomber.io/broken\nhttps://ploomber.io/')
    Path('nested', 'dir',
         'another.rst').write_text('https://ploomber.io/broken-another')

    assert links.find_broken_in_files(extensions) == expected
