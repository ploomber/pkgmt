import pytest
import subprocess

from pkgmt import modified

@pytest.fixture(scope="session", autouse=True)
def setup():
    # fixture setup code
    # Creates a git branch, adds a file and commits it
    cmd = """
    git checkout main;
    git checkout -b test_modified_doc;
    mkdir -p test_doc1;
    touch test_doc1/test_modified.txt;
    mkdir -p test_doc2;
    touch test_doc2/test_modified.txt;
    git add .;
    git commit -m "test_modified";
    """
    subprocess.run(cmd, shell=True)

    yield

    # fixture teardown code
    # Deletes the git branch
    cmd = """
    git checkout main;
    git branch -D test_modified;
    """
    subprocess.run(cmd, shell=True)



@pytest.mark.parametrize(
    "base_branch, exclude_path, returncode",
    [
        [
            "main",
            ["doc1"],
            1,
        ],
        [
            "main",
            ["doc1","doc2"],
            0,
        ]
    ]
)
def test_check_modified( base_branch, exclude_path, returncode):

    assert modified.check_modified(base_branch, exclude_path, debug=True) == returncode
    # subprocess.run(clean, shell=True)