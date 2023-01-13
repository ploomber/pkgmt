from unittest.mock import ANY
from pathlib import Path
import re

from pkgmt import config

_PREFIXES = {"[API Change]", "[Feature]", "[Fix]", "[Doc]"}


def _replace_issue_number_with_links(url, text):
    # taken from jupytext/tests/test_changelog.py
    return re.sub(
        r"([^\[])#([0-9]+)",
        r"\1[#\2](" + url + r"\2)",
        text,
    )


def _expand_github_from_text(text):
    """Convert strings with the #{number} format into their"""
    cfg = config.load()
    url = f'https://github.com/{cfg["github"]}/issues/'
    return _replace_issue_number_with_links(url, text)


def expand_github_from_changelog(path="CHANGELOG.md"):
    path = Path(path)
    changelog = path.read_text()
    changelog_ = _expand_github_from_text(changelog)
    path.write_text(changelog_)


# functions for checking CHANGELOG contents


def _find_first_subheading(tree):
    subheading = {
        "type": "heading",
        "children": [{"type": "text", "text": ANY}],
        "level": 2,
    }

    for idx, element in enumerate(tree):
        if element == subheading:
            return idx

    raise ValueError("Error parsing CHANGELOG: Could not find an H2 heading")


def _find_first_list_after(tree, idx):
    for element in tree[2:]:
        if element["type"] == "list":
            return element

    raise ValueError(
        "Error parsing CHANGELOG: Could not find a list after the H2 heading"
    )


def _extract_text_from_items(list_):
    return [item["children"][0]["children"][0]["text"] for item in list_["children"]]


def _get_latest_changelog_entries(text):
    # NOTE: this requires mistune 2
    import mistune

    markdown = mistune.create_markdown(renderer=mistune.AstRenderer())
    tree = markdown(text)

    idx_subheading = _find_first_subheading(tree)
    changes = _find_first_list_after(tree, idx_subheading)
    items_text = _extract_text_from_items(changes)
    return items_text


def _valid_item(item):
    return any(item.startswith(prefix) for prefix in _PREFIXES)


def check_latest_changelog_entries(text):
    invalid = []

    for item in _get_latest_changelog_entries(text):
        if not _valid_item(item):
            invalid.append(item)

    if invalid:
        raise ValueError(
            f"Found invalid items: {invalid!r}. All items must start "
            f"with one of: {_PREFIXES}"
        )

    return True
