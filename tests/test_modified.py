import pytest
from pkgmt import fail_if_modified


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
    assert (
        fail_if_modified.check_modified(base_branch, exclude_path, debug=True)
        == returncode
    )


def test_check_modified_2(tmp_package_modi_2):
    assert fail_if_modified.check_modified("main", ["doc"], debug=True) == 0
