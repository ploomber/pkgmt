import re
import ast
import datetime
import subprocess

from pathlib import Path

import click

from pkgmt.versioner.util import complete_version_string, find_package_and_version_file


def replace_in_file(path_to_file, original, replacement):
    """Replace string in file"""
    with open(path_to_file, "r+") as f:
        content = f.read()
        updated = content.replace(original, replacement)
        f.seek(0)
        f.write(updated)
        f.truncate()


def call(*args, **kwargs):
    return subprocess.run(*args, **kwargs, check=True)


def make_header(content, path, add_date=False):
    if add_date:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        content += f" ({today})"

    if path.suffix == ".md":
        return f"## {content}"
    elif path.suffix == ".rst":
        return f"{content}\n" + "-" * len(content)
    else:
        raise ValueError("Unsupported format, must be .rst or .md")


class Versioner:
    def __init__(self, project_root="."):
        self.project_root = project_root or "."
        package_name, PACKAGE, version_file_name = find_package_and_version_file(
            self.project_root
        )
        self.package_name = package_name
        self.PACKAGE = PACKAGE
        if Path(self.project_root, "CHANGELOG.rst").exists():
            self.path_to_changelog = Path(self.project_root, "CHANGELOG.rst")
        elif Path(self.project_root, "CHANGELOG.md").exists():
            self.path_to_changelog = Path(self.project_root, "CHANGELOG.md")
        else:
            self.path_to_changelog = None
        self.version_file = version_file_name

    def get_version_file_path(self):
        """Returns the version file path from project root"""
        return str(self.PACKAGE / self.version_file)

    def current_version(self):
        """Returns the current version in version file"""
        _version_re = re.compile(r"__version__\s+=\s+(.*)")

        with open(self.PACKAGE / self.version_file, "rb") as f:
            try:
                VERSION = str(
                    ast.literal_eval(
                        _version_re.search(f.read().decode("utf-8")).group(1)
                    )
                )
            except AttributeError:
                raise click.ClickException(
                    f"Please add version string in "
                    f"{self.get_version_file_path()}, e.g., __version__ = '0.1dev'"
                )
            except SyntaxError:
                raise click.ClickException(
                    f"Could not find __version__ value in "
                    f"{self.get_version_file_path()}. Please add in the format"
                    f" __version__ = '0.1dev'"
                )

        return VERSION

    def release_version(self):
        """
        Returns a release version number
        e.g. 2.4.4dev -> v.2.2.4
        """
        current = self.current_version()

        if "dev" not in current:
            raise ValueError("Current version is not a dev version")

        new = current.replace("dev", "")

        return complete_version_string(new)

    def bump_up_version(self):
        """
        Gets a the current released version and returns the next value.
        e.g. 1.2.5 -> 1.2.6dev

        Notes
        -----
        If a doing a pre-release (e.g., 1.0b1), the new version returns to dev
        (e.g., 1.0b1 -> 1.0dev)
        """
        # Get current version
        current = self.current_version()

        # pre-releases
        for pre in ["a", "b", "rc"]:
            if pre in current:
                prefix = current.split(pre)[0]
                return f"{prefix}dev"

        if "dev" in current:
            raise ValueError(
                "Current version is dev version, new dev "
                "versions can only be made from release versions"
            )

        # Get Z from X.Y.Z and sum 1
        tokens = current.split(".")

        # if just released a major version, add a 0 so we bump up a subversion
        # e.g. from 0.8 -> 0.8.0, then new dev version becomes 0.8.1dev
        if len(tokens) == 2:
            tokens.append("0")

        new_subversion = int(tokens[-1]) + 1

        # Replace new_subversion in current version
        tokens[-1] = str(new_subversion)
        new_version = ".".join(tokens) + "dev"

        return new_version

    def commit_version(self, new_version, msg_template, tag=False, push=True):
        """
        Replaces version in  __init__ and optionally creates a tag in the git
        repository (also saves a commit)

        Parameters
        ----------
        tag: bool, default=False
            If True, it adds ``new_version`` as tag.

        push : bool, default=True
            If True, it pushes the commit with ``new_version`` and the tag
        """
        current = self.current_version()

        # replace new version in version file
        replace_in_file(self.PACKAGE / self.version_file, current, new_version)

        # Run git add and git status
        print("Adding new changes to the repository...")
        call(["git", "add", "--all"])
        call(["git", "status"])

        # Commit repo with updated dev version
        print("Creating new commit release version...")
        msg = msg_template.format(
            package_name=self.package_name, new_version=new_version
        )
        call(["git", "commit", "-m", msg])

        # Create tag
        if tag:
            print("Creating tag {}...".format(new_version))
            message = msg_template.format(
                package_name=self.package_name, new_version=new_version
            )
            call(["git", "tag", "-a", new_version, "-m", message])

            if push:
                print("Pushing tags...")
                call(["git", "push", "origin", new_version, "--no-verify"])
        elif push:
            # no tag but push
            print("Pushing...")
            call(["git", "push", "--no-verify"])

    def update_changelog_release(self, new_version):
        """Updates changelog file, adding a new section"""
        current_version = self.current_version()

        # update CHANGELOG header
        header_current = make_header(
            current_version, self.path_to_changelog, add_date=False
        )

        header_new = make_header(new_version, self.path_to_changelog, add_date=True)

        replace_in_file(self.path_to_changelog, header_current, header_new)

    def add_changelog_new_dev_section(self, dev_version):
        if self.path_to_changelog:
            if self.path_to_changelog.suffix == ".rst":
                start_current = "CHANGELOG\n========="
            else:
                start_current = "# CHANGELOG"

            new_header = make_header(dev_version, self.path_to_changelog)
            start_new = f"{start_current}\n\n{new_header}"
            replace_in_file(self.path_to_changelog, start_current, start_new)
        else:
            print("No CHANGELOG.{rst,md} found, skipping changelog editing...")
