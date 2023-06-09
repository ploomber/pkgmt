import pytest
from pkgmt import fail_if_modified, fail_if_not_modified
from pathlib import Path


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
def test_check_modified_ex(tmp_package_modi, base_branch, exclude_path, returncode):
    assert (
        fail_if_modified.check_modified(base_branch, exclude_path, debug=True)
        == returncode
    )


def test_check_modified_ex_2(tmp_package_modi_2):
    assert fail_if_modified.check_modified("main", ["doc"], debug=True) == 0


@pytest.mark.parametrize(
    "base_branch, include_path, returncode",
    [
        [
            "main",
            ["test_doc1"],
            0,
        ],
        [
            "main",
            ["test_doc1", "test_doc2"],
            0,
        ],
        [
            "main",
            ["src"],
            1,
        ],
        [
            "main",
            ["test_doc1", "test_doc2", "src"],
            1,
        ],
    ],
)
def test_check_modified_in(tmp_package_modi, base_branch, include_path, returncode):
    assert (
        fail_if_not_modified.check_modified(base_branch, include_path, debug=True)
        == returncode
    )


@pytest.mark.parametrize(
    "base_branch, include_path, returncode",
    [
        [
            "main",
            [str(Path("doc", "another.txt"))],
            0,
        ],
        [
            "main",
            [str(Path("something", "file.txt"))],
            1,
        ],
    ],
)
def test_check_modified_in_2(tmp_package_modi_2, base_branch, include_path, returncode):
    assert (
        fail_if_not_modified.check_modified(base_branch, include_path, debug=True)
        == returncode
    )
