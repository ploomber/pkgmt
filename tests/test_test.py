from pathlib import Path

from pkgmt import test


def test_markdown(tmp_empty):
    Path("file.md").write_text(
        """
```python
1 + 1
```
"""
    )
    nb = test.markdown("file.md", inplace=True)

    assert nb.cells[0].outputs[0]["data"]["text/plain"] == "2"


def test_markdown_in_tmp_directory(tmp_empty):
    Path("some-file.txt").write_text("hello!")

    Path("file.md").write_text(
        """
```python
from pathlib import Path
print(Path('some-file.txt').read_text())
```
"""
    )
    nb = test.markdown("file.md", inplace=False)

    assert nb.cells[0].outputs[0]["text"] == "hello!\n"
