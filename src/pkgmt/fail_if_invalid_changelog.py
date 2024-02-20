import subprocess
import argparse
import sys
from pathlib import Path

from pkgmt import changelog


def latest_changelog_header(base_branch):
    changelog_contents = (
        subprocess.check_output(f"git show {base_branch}:CHANGELOG.md", shell=True)
        .decode("utf-8")
        .split()
    )
    for line in changelog_contents:
        if "dev" in line:
            return line.strip()


def check_modified(base_branch, debug=False):
    latest_section_main = latest_changelog_header(base_branch)
    text = Path("CHANGELOG.md").read_text()
    changelog_parser = changelog.CHANGELOG(text)
    latest_section_current = changelog_parser.get_first_subheading()[1].strip()
    if latest_section_main != latest_section_current:
        print(
            f"Latest section in CHANGELOG.md "
            f"not up-to-date. Latest section in "
            f"{base_branch}: {latest_section_main}"
        )
        return 1
    cmd = f"git diff -U0 {base_branch}... -- CHANGELOG.md"
    try:
        out = subprocess.check_output(cmd, shell=True).decode("utf-8")
        all_diff = []
        for line in out.split("\n"):
            if not (line.startswith("+++") or line.startswith("---")):
                all_diff.append(line.strip())
        git_removals = [
            line[1:].strip()
            for line in all_diff
            if line.startswith("-")
            if line[1:].strip() != ""
        ]
        git_additions = [
            line[1:].strip()
            for line in all_diff
            if line.startswith("+")
            if line[1:].strip() != ""
        ]

        if len(git_additions) == 0 or out == "" and debug:
            print(f"CHANGELOG.md has not been modified with respect to '{base_branch}'")
            return 1

        if git_removals:
            print(
                f"These entries have been removed: "
                f"{'; '.join(git_removals)}. Please revert the changes."
            )
            return 1

        if git_additions:
            latest_entries = changelog_parser.get_latest_changelog_section()
            for line in git_additions:
                if line:
                    try:
                        extracted_text = changelog.CHANGELOG(
                            line
                        ).extract_text_from_entry()
                    except KeyError:
                        continue
                    if extracted_text[0] not in latest_entries:
                        print(
                            f"Entry '{line}' should be added "
                            f"to section {latest_section_main}"
                        )
                        return 1

                    elif extracted_text[0].strip() == "":
                        print(f"You have added an empty entry: {line}")
                        return 1

    except subprocess.CalledProcessError:
        pass
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check if proper modifications has been done to CHANGELOG.md"
    )
    parser.add_argument(
        "-b", "--base-branch", default="main", help="Base branch to compare against"
    )
    parser.add_argument("--debug", action="store_true", help="Print debug info")

    args = parser.parse_args()
    return_code = check_modified(args.base_branch, debug=args.debug)
    sys.exit(return_code)
