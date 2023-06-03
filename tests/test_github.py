import pytest

from pkgmt import github


def test_get_pr():
    assert github.get_pr("ploomber", "ploomber", 1071)


@pytest.mark.parametrize(
    "pr_number, expected_repo, expected_branch",
    [
        [
            1071,
            "https://github.com/tonykploomber/ploomber",
            "1070-noqa-coming-up-on-docs",
        ],
        [
            1044,
            "https://github.com/ploomber/ploomber",
            "cloud_stats",
        ],
    ],
    ids=[
        "fork",
        "branch",
    ],
)
def test_get_repo_and_branch_for_pr(pr_number, expected_repo, expected_branch):
    repo, branch = github.get_repo_and_branch_for_pr("ploomber", "ploomber", pr_number)

    assert repo == expected_repo
    assert branch == expected_branch


@pytest.mark.parametrize(
    "pr_number, expected_repo, expected_branch",
    [
        [
            "1071",
            "https://github.com/tonykploomber/ploomber",
            "1070-noqa-coming-up-on-docs",
        ],
        [
            "1044",
            "https://github.com/ploomber/ploomber",
            "cloud_stats",
        ],
    ],
    ids=[
        "fork",
        "branch",
    ],
)
def test_get_repo_and_branch_for_readthedocs(
    monkeypatch, pr_number, expected_repo, expected_branch
):
    monkeypatch.setenv("READTHEDOCS_VERSION_NAME", pr_number)

    repo, branch = github.get_repo_and_branch_for_readthedocs(
        "https://github.com/ploomber/ploomber", default_branch="master"
    )

    assert repo == expected_repo
    assert branch == expected_branch
