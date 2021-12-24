from pathlib import Path
import re

from pkgmt import config


def _replace_issue_number_with_links(url, text):
    # taken from jupytext/tests/test_changelog.py
    return re.sub(
        r"([^\[])#([0-9]+)",
        r"\1[#\2](" + url + r"\2)",
        text,
    )


def _expand_github_from_text(text):
    """Convert strings with the #{number} format into their
    """
    cfg = config.load()
    url = f'https://github.com/{cfg["github"]}/issues/'
    return _replace_issue_number_with_links(url, text)


def expand_github_from_changelog(path='CHANGELOG.md'):
    path = Path(path)
    changelog = path.read_text()
    changelog_ = _expand_github_from_text(changelog)
    path.write_text(changelog_)
