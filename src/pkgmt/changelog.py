from unittest.mock import ANY
from pathlib import Path
import re
from enum import IntEnum
from functools import total_ordering
from copy import deepcopy
import click


try:
    import mistune
    from mistune.renderers.markdown import MarkdownRenderer
    from mistune.core import BlockState
    from mistune.inline_parser import InlineParser
except ModuleNotFoundError:
    mistune = None
    MarkdownRenderer = None
    BlockState = None
    InlineParser = object

from pkgmt import config
from pkgmt.versioner import util
from pkgmt.versioner.versioner import Versioner
from pkgmt._format import pretty_iterator
from pkgmt.exceptions import ProjectValidationError

_PREFIXES = {"[API Change]", "[Feature]", "[Fix]", "[Doc]"}


class CustomInlineParser(InlineParser):
    """
    Custom parser to prevent escaping characters inside `code spans`
    """

    def parse_codespan(self, m, state) -> int:
        marker = m.group(0)
        # require same marker with same length at end

        pattern = re.compile(r"(.*?(?:[^`]))" + marker + r"(?!`)", re.S)

        pos = m.end()
        m = pattern.match(state.src, pos)
        if m:
            end_pos = m.end()
            code = m.group(1)
            # Line endings are treated like spaces
            code = code.replace("\n", " ")
            if len(code.strip()):
                if code.startswith(" ") and code.endswith(" "):
                    code = code[1:-1]
            # removed the escaping here
            state.append_token({"type": "codespan", "raw": code})
            return end_pos
        else:
            state.append_token({"type": "text", "raw": marker})
            return pos


def _replace_issue_number_with_links(url, text):
    # taken from jupytext/tests/test_changelog.py
    return re.sub(
        r"([^\[])#([0-9]+)",
        r"\1[#\2](" + url + r"\2)",
        text,
    )


def _replace_handles_with_links(text):
    pattern = r"(?<!\[)@([\w\-_]+)(?!\]\(https:\/\/github\.com\/\w+\))"
    repl = r"[\g<0>](https://github.com/\g<1>)"
    return re.sub(pattern, repl, text)


def _expand_github_from_text(text):
    """Convert strings with the #{number} format into their"""
    cfg = config.Config.from_file("pyproject.toml")
    url = f'https://github.com/{cfg["github"]}/issues/'
    return _replace_handles_with_links(_replace_issue_number_with_links(url, text))


def expand_github_from_changelog(path="CHANGELOG.md"):
    path = Path(path)
    changelog = path.read_text()
    changelog_ = _expand_github_from_text(changelog)
    path.write_text(changelog_)


# functions for checking CHANGELOG contents


def _find_first_list_after(tree, idx):
    for idx, element in enumerate(tree[idx + 1 :], start=idx + 1):
        if element["type"] == "heading":
            return None, idx
        elif element["type"] == "list":
            return element, idx

    raise ProjectValidationError(
        "Error parsing CHANGELOG: Could not find a list after the H2 heading"
    )


def _extract_text_from_token(token):
    if token["type"] in {"text", "codespan"}:
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


@total_ordering
class ListItem:
    def __init__(self, token) -> None:
        self.token = token
        self.text = "".join(
            [_extract_text_from_token(ch) for ch in token["children"][0]["children"]]
        )
        result = re.search(r"(\[API Change\]|\[Feature\]|\[Fix\]|\[Doc\])", self.text)
        self.type = result.group()
        self.type_enum = ListItemType.from_str(self.type)

    def __eq__(self, other):
        return self.type_enum == other.type_enum

    def __lt__(self, other):
        return self.type_enum < other.type_enum

    def __repr__(self) -> str:
        return f"LisItem({self.text!r})"


class ListItemType(IntEnum):
    api_change = 1
    feature = 2
    fix = 3
    doc = 4

    @classmethod
    def from_str(cls, s):
        mapping = {
            "[API Change]": 1,
            "[Feature]": 2,
            "[Fix]": 3,
            "[Doc]": 4,
        }
        return mapping[s]


class CHANGELOG:
    """Run several checks in the CHANGELOG.md file"""

    def __init__(self, text, project_root=".") -> None:
        if not mistune:
            raise ModuleNotFoundError(
                "Checking CHANGELOG.md requires mistune 3. "
                "Install it with: pip install 'pkgmt[check]'"
            )

        if mistune.__version__[0] != "3":
            raise ModuleNotFoundError(
                "Checking CHANGELOG.md requires mistune 3. "
                f"You have {mistune.__version__}. Install it with: "
                "pip install 'pkgmt[check]'"
            )

        self.text = text

        markdown = mistune.Markdown(
            renderer=None, inline=CustomInlineParser(hard_wrap=False), plugins=None
        )
        self.tree = markdown(text)

        versioner = Versioner(project_root=project_root)
        self.version_file = versioner.get_version_file_path()
        self.current = versioner.current_version()

    @classmethod
    def from_path(cls, path, project_root="."):
        return cls(text=Path(path).read_text(), project_root=project_root)

    def sort_last_section(self):
        """Sorts last section depending on the prefix"""
        self.check_latest_changelog_entries()

        idx_subheading, _ = self.get_first_subheading()
        list_, idx = _find_first_list_after(self.tree, idx_subheading)
        renderer = MarkdownRenderer()

        if list_:
            li = sorted([ListItem(ch) for ch in list_["children"]])
            tree = deepcopy(self.tree)
            tree[idx]["children"] = [item.token for item in li]
            return renderer(tree, state=BlockState())
        else:
            # list is empty, nothing to sort
            return self.text

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

        raise ProjectValidationError(
            "Error parsing CHANGELOG: Could not find an H2 heading"
        )

    def get_latest_changelog_section(self):
        """Gets the elements in the first section (below the first H2 heading)"""
        idx_subheading, _ = self.get_first_subheading()
        changes, _ = _find_first_list_after(self.tree, idx_subheading)

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
            raise ProjectValidationError(
                "[Unexpected version] Expected a major version since there is at least "
                f"one [API Change] CHANGELOG entry, got minor version: {self.current!r}"
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
            _PREFIXES_OUT = pretty_iterator(_PREFIXES)
            invalid_out = pretty_iterator(invalid)
            raise ProjectValidationError(
                f"[Invalid CHANGELOG] Changelog items must start with one "
                f"of: {_PREFIXES_OUT}. Fix the following entries: {invalid_out}"
            )

        return True

    def check_consistent_changelog_and_version(self):
        """
        Check the latest section in CHANGELOG.md matches the __version__ string
        """
        _, subheading = self.get_first_subheading()

        # when making stable releases, the format is: "{version} {date}"
        # in such cases, we only compare the "{version}" part
        date_match = re.match(r"([\w\.]+)( \([0-9]{4}-[0-9]{2}-[0-9]{2}\))", subheading)

        if (date_match and date_match.group(1) != self.current) or (
            date_match is None and subheading != self.current
        ):
            raise ProjectValidationError(
                "[Inconsistent version] Version in  top section in "
                f"CHANGELOG is {subheading!r}, "
                f"but version in {self.version_file} is {self.current!r}, "
                "fix them so they match"
            )

    def check(self, *, verbose=False):
        """Runs all checks"""
        errors = []

        for function, name in (
            (self.check_latest_changelog_entries, "CHANGELOG entries prefixes"),
            (
                self.check_consistent_changelog_and_version,
                "CHANGELOG and __init__.py consistency",
            ),
            (self.check_consistent_dev_version, "consistent dev version"),
        ):
            try:
                function()
            except Exception as e:
                errors.append(str(e))
                if verbose:
                    click.secho(f"Checking {name}... ERROR!", fg="red")
            else:
                if verbose:
                    click.secho(f"Checking {name}... OK!", fg="green")

        if errors:
            errors_ = "\n\n".join(f"- {e}" for e in errors)
            raise ProjectValidationError(
                f"Found the following errors in the project:\n{errors_}"
            )
