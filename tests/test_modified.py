import pytest
from pkgmt import modified


@pytest.mark.parametrize(
    "base_branch, exclude_path, returncode",
    [
        [
            "main",
            ["test_doc1"],
            1,
        ],
        [
            "main",
            ["test_doc1", "test_doc2"],
            0,
        ],
    ],
)
def test_check_modified(tmp_package_modi, base_branch, exclude_path, returncode):
    assert modified.check_modified(base_branch, exclude_path, debug=True) == returncode
