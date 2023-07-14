"""
Managing project versions
"""
import sys
import shutil
import subprocess
from pathlib import Path
import click

from pkgmt.config import load
from pkgmt.changelog import expand_github_from_changelog, CHANGELOG
from pkgmt.versioner.versioner import Versioner
from pkgmt.versioner.util import complete_version_string, is_pre_release
from pkgmt.deprecation import Deprecations


VALID_KEYS = ["github", "version", "package_name"]
VALID_VERSION_KEYS = ["version_file", "tag", "push"]


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


def delete_dirs(*dirs):
    for dir_ in dirs:
        if Path(dir_).exists():
            shutil.rmtree(dir_)


def _input(prompt):
    return input(prompt)


def input_str(prompt, default):
    separator = " " if len(prompt.splitlines()) == 1 else "\n"
    response = _input(prompt + f"{separator}(Default: {default}): ")

    if not response:
        response = default

    return response


def input_confirm(prompt, abort):
    separator = " " if len(prompt.splitlines()) == 1 else "\n"
    response_raw = _input(prompt + f"{separator}Confirm? [y/n]: ")
    response = response_raw in {"y", "Y", "yes"}

    if not response and abort:
        print("Aborted!")
        sys.exit(1)

    return response


def validate_version_string(version):
    if not len(version):
        raise ValueError(f"Got invalid empty version string: {version!r}")

    if version[0] not in "0123456789":
        raise ValueError(
            f"Got invalid version string: {version!r} "
            "(first character must be numeric)"
        )

    return complete_version_string(version)


def validate_config(cfg):
    """
    Function to validate top level and version keys in
    config file.
    """
    keys = list(cfg.keys())
    for key in keys:
        if key not in VALID_KEYS:
            raise click.ClickException(
                f"Invalid key '{key}' in"
                f" pyproject.toml file. Valid keys are : "
                f"{', '.join(VALID_KEYS)}"
            )

        if cfg.get("version", {}):
            version_keys = list(cfg.get("version").keys())
            for key in version_keys:
                if key not in VALID_VERSION_KEYS:
                    raise click.ClickException(
                        f"Invalid version key '{key}' in"
                        f" pyproject.toml file. Valid keys are : "
                        f"{', '.join(VALID_VERSION_KEYS)}"
                    )


def read_version_config(cfg):
    """
    Function to return tag and push from
    pyproject.toml if provided by user.
    Example file:
    [tool.pkgmt]
    github = "repository/package"
    version = {version_file = "/app/_version.py", tag=True, push=False}
    """
    tag = cfg.get("version", {}).get("tag", None)
    push = cfg.get("version", {}).get("push", None)
    if tag is not None and not isinstance(tag, bool):
        raise click.ClickException(
            "Type of 'tag' key in pyproject.toml is invalid. "
            "It should be lowercase boolean : true / false"
        )
    if push is not None and not isinstance(push, bool):
        raise click.ClickException(
            "Type of 'push' key in pyproject.toml is invalid. "
            "It should be lowercase boolean : true / false"
        )
    if tag:
        print(f"Reading tag = {tag} from pyproject.toml")
    if push:
        print(f"Reading push = {push} from pyproject.toml")
    return tag, push


def version(
    project_root=".",
    tag=True,
    yes=False,
    push=True,
    target=None,
):
    """

    Function to update latest stable version in version
    file to new development version.

    Parameters
    ----------
    tag : bool, default=True
        Tags the commit with the stable version

    yes : bool, default=False
        Skips user prompt before applying changes

    push : bool, default=True
        Pushes the changes to the remote repository

    target : {None, "stable"}, default=None
        If None, it assumes the repository is in a dev version, so it creates a
        stable version and a new dev version. If stable, it assumes the repo is in a
        dev version and creates a stable version (skipping bumping to a new dev
        version)
    """

    _git_checkout_main_branch(pull=True)

    pending = subprocess.check_output(["git", "status", "--short"])

    if pending:
        raise click.ClickException(
            "Cannot run 'pkgmt version': you have pending files to commit. "
            "Commit them or discard them and try again.\nDetected files:"
            f"\n{pending.decode()}"
        )

    cfg = load()

    validate_config(cfg)

    cfg_tag, cfg_push = read_version_config(cfg)
    tag = cfg_tag if cfg_tag is not None else tag
    push = cfg_push if cfg_push is not None else push

    versioner = Versioner(project_root)

    changelog_md_exists = (
        versioner.path_to_changelog and versioner.path_to_changelog.suffix == ".md"
    )

    if changelog_md_exists:
        # check changelog
        CHANGELOG.from_path(
            path=versioner.path_to_changelog,
            project_root=project_root,
        ).check()

        # look for deprecations
        Deprecations(root_dir=project_root).check()

    current = versioner.current_version()
    release = versioner.release_version()

    if yes:
        print(f"Releasing version: {release}")
    else:
        release = input_str(
            "Current version in setup.py is {current}. Enter"
            " release version".format(current=current),
            default=release,
        )

    release = validate_version_string(release)

    if versioner.path_to_changelog and not is_pre_release(release):
        versioner.update_changelog_release(release)

        changelog = versioner.path_to_changelog.read_text()

        if not yes:
            input_confirm(
                f"\n{versioner.path_to_changelog} content:" f"\n\n{changelog}\n",
                abort=True,
            )

    # Expand github links and sort secions
    if changelog_md_exists:
        expand_github_from_changelog(path=versioner.path_to_changelog)

        # sort changelog entries
        changelog_sorted = CHANGELOG.from_path(
            path=versioner.path_to_changelog,
            project_root=project_root,
        ).sort_last_section()
        Path(versioner.path_to_changelog).write_text(changelog_sorted)

    else:
        print("Skipping CHANGELOG processing (only supported in .md files)")

    # Replace version number and create tag
    print("Commiting release version: {}".format(release))
    versioner.commit_version(
        release,
        msg_template="{package_name} release {new_version}",
        tag=tag,
        push=push,
    )

    if target == "stable":
        print(f"Version {release} was created.")
        return

    # Create a new dev version and save it
    bumped_version = versioner.bump_up_version()

    if not is_pre_release(release):
        print("Creating new section in CHANGELOG...")
        versioner.add_changelog_new_dev_section(bumped_version)

    print("Commiting dev version: {}".format(bumped_version))
    versioner.commit_version(
        bumped_version,
        msg_template="Bumps up {package_name} to version {new_version}",
        tag=False,
        push=push,
    )

    print("Version {} was created, you are now in {}".format(release, bumped_version))


def _git_checkout_main_branch(pull=False):
    try:
        call(["git", "checkout", "main"])
    except subprocess.CalledProcessError:
        try_master = True
    else:
        try_master = False

    if try_master:
        try:
            call(["git", "checkout", "master"])
        except subprocess.CalledProcessError:
            pass

    if pull:
        call(["git", "pull"])


def upload(tag, production, yes=False):
    """
    Check outs a tag, uploads to PyPI
    """
    print("Checking out tag {}".format(tag))
    call(["git", "checkout", tag])

    versioner = Versioner()
    current = versioner.current_version()

    if not yes:
        input_confirm(
            "Version in {} tag is {}. Do you want to continue?".format(tag, current),
            abort=True,
        )

    # create distribution
    delete_dirs("dist", "build", f"{versioner.PACKAGE}.egg-info")
    call(["python", "setup.py", "bdist_wheel", "sdist"])

    print("Publishing to PyPI...")

    if not production:
        call(
            [
                "twine",
                "upload",
                "--repository-url",
                "https://test.pypi.org/legacy/",
                "dist/*",
            ]
        )
    else:
        call(["twine", "upload", "dist/*"])

    _git_checkout_main_branch()

    if production:
        click.secho("Published to PyPI.", fg="green")
    else:
        click.secho("Published to PyPI test server.", fg="yellow")
