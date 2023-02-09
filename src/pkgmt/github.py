import os
import requests


def get_pr(owner, repo, number):
    """Get pull request information"""
    return requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    ).json()


def get_repo_and_branch_for_pr(owner, repo, number):
    """Return the fork repo and branch branch for a given pull request number"""
    response = get_pr(owner, repo, number)
    full_name = response["head"]["repo"]["full_name"]
    ref = response["head"]["ref"]
    url = f"https://github.com/{full_name}"
    return url, ref


def get_repo_and_branch_for_readthedocs(repository_url, default_branch="master"):
    """Get repository and branch for the current readthedocs build"""
    # TODO: handle the case where READTHEDOCS_VERSION_NAME == "stable"
    version_name = os.environ.get("READTHEDOCS_VERSION_NAME", default_branch)

    if version_name == "latest":
        version_name = default_branch

    print(f"Version: {version_name}")

    username, reponame = repository_url.split("/")[-2:]

    try:
        # check if a number (this means the build is from a PR)
        int(version_name)
    except ValueError:
        repository_branch = version_name
    else:
        repository_url, repository_branch = get_repo_and_branch_for_pr(
            username, reponame, version_name
        )

    print(f"URL: {repository_url}. Branch: {repository_branch}")

    return repository_url, repository_branch
