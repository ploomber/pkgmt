from unittest.mock import ANY
from pathlib import Path
import re


import mistune

from pkgmt import config
from pkgmt.versioner.versionersetup import VersionerSetup
from pkgmt.versioner import util

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


def _find_first_list_after(tree, idx):
    for element in tree[idx + 1 :]:
        if element["type"] == "heading":
            return None
        elif element["type"] == "list":
            return element

    raise ValueError(
        "Error parsing CHANGELOG: Could not find a list after the H2 heading"
    )


def _extract_text_from_token(token):
    if token["type"] == "text":
        return token["raw"]
    elif token["type"] == "link":
        return token["children"][0]["raw"]
    else:
        raise NotImplementedError(f"Unable to extract text from token: {token}")


def _extract_text_from_item(item):
    return "".join(
        [_extract_text_from_token(ch) for ch in item["children"][0]["children"]]
    )


def _extract_text_from_items(list_):
    return [_extract_text_from_item(item) for item in list_["children"]]


def _valid_item(item):
    return any(item.startswith(prefix) for prefix in _PREFIXES)


def _breaks_api(items):
    return any(item.startswith("[API Change]") for item in items)


class CHANGELOG:
    """Run several checks in the CHANGELOG.md file"""

    def __init__(self, text) -> None:
        markdown = mistune.create_markdown(renderer=None)
        self.tree = markdown(text)

        versioner = VersionerSetup()
        self.current = versioner.current_version()

    def sort_last_section(self):
        idx_subheading, _ = self.get_first_subheading()
        changes = _find_first_list_after(self.tree, idx_subheading)
        return changes

    def get_first_subheading(self):
        """Find the first H2 heading. Returns index (in the tree) and text"""
        subheading = {
            "type": "heading",
            "attrs": {"level": 2},
            "style": "axt",
            "children": [{"type": "text", "raw": ANY}],
        }

        for idx, element in enumerate(self.tree):
            if element == subheading:
                return idx, element["children"][0]["raw"]

        raise ValueError("Error parsing CHANGELOG: Could not find an H2 heading")

    def get_latest_changelog_section(self):
        """Gets the elements in the first section (below the first H2 heading)"""
        idx_subheading, _ = self.get_first_subheading()
        changes = _find_first_list_after(self.tree, idx_subheading)

        if changes:
            items_text = _extract_text_from_items(changes)
            return items_text
        else:
            return []

    def check_consistent_dev_version(self):
        """
        Ensures that there is a major development version set if there's at least one
        [API Change] entry in the latest CHANGELOG section
        """
        changelog_entries = self.get_latest_changelog_section()

        if _breaks_api(changelog_entries) and not util.is_major_version(self.current):
            raise ValueError(
                "Expected a major version since there is at least "
                f"one [API Change] changelog entry, got version: {self.current}"
            )

    def check_latest_changelog_entries(self):
        """
        Ensures the entries in the latest CHANGELOG section have the right prefixes
        """
        invalid = []

        for item in self.get_latest_changelog_section():
            if not _valid_item(item):
                invalid.append(item)

        if invalid:
            raise ValueError(
                f"Found invalid items: {invalid!r}. All items must start "
                f"with one of: {_PREFIXES}"
            )

        return True

    def check_consistent_changelog_and_version(self):
        """
        Check the latest section in CHANGELOG.md matches the __version__ string
        """
        _, subheading = self.get_first_subheading()

        if subheading != self.current:
            raise ValueError(
                "Inconsistent version. Version in  top section in "
                f"CHANGELOG is {subheading}. Version in __init__.py is {self.current}"
            )

    def check(self):
        """Runs all checks"""
        errors = []

        for function in (
            self.check_consistent_dev_version,
            self.check_latest_changelog_entries,
            self.check_consistent_changelog_and_version,
        ):
            try:
                function()
            except Exception as e:
                errors.append(str(e))

        if errors:
            errors_ = "\n\n".join(errors)
            raise ValueError(f"Errors:\n{errors_}")
