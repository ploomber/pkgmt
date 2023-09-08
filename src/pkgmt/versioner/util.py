import re
import os
import click
import warnings
from pathlib import Path


def is_pre_release(version):
    return "a" in version or "b" in version or "rc" in version


def is_major_version(version):
    _, major, minor = complete_version_string(version.replace("dev", "")).split(".")
    return (minor == "0") or (major == "0" and minor == "0")


def _split_prerelease_part(version):
    if is_pre_release(version):
        prerelease_part = re.search(r"(a|b|rc)\d+", version).group(0)
    else:
        prerelease_part = ""

    return version.replace(prerelease_part, ""), prerelease_part


def complete_version_string(version):
    part_version, part_prerelease = _split_prerelease_part(version)
    elements = len(part_version.split("."))

    if elements < 3:
        missing = 3 - elements
        suffix = ".".join(["0"] * missing)
        version = f"{part_version}.{suffix}"

    if not version.endswith(part_prerelease):
        version = version + part_prerelease

    return version


def find_package_in_src(project_root="."):
    """
    Function to find the path of the package inside src directory. If multiple packages
    found, first is selected.

    Parameters
    ----------
    project_root: str, root folder of the project.
                  Default is "."

    Returns
    -------
    package_name
        Package name of the project (e.g., "some_package")

    path_to_package
        Path to the package (e.g., "src/some_package")
    """

    path_to_src = Path(project_root, "src")

    if not path_to_src.is_dir():
        raise NotADirectoryError(
            f"Expected a directory at {str(path_to_src)!r} but it doesn't exist"
        )

    dirs = sorted(
        [
            f
            for f in os.listdir(path_to_src)
            if Path("src", f).is_dir()
            and not f.endswith(".egg-info")
            and Path(f).name != "__pycache__"
        ]
    )

    if len(dirs) != 1:
        warnings.warn("Found more than one dir, " f"choosing the first one: {dirs[0]}")

    package_name = dirs[0]
    path_to_package = path_to_src / package_name
    return package_name, path_to_package


def find_package_of_version_file(version_file_path):
    """
    Function to find the path of the package inside src directory

    Parameters
    ----------

    version_file_path: str
        Path of the file in which __version__ string is stored

    project_root: str
        Root folder of the project. Default is "."

    Returns
    -------
    name and path of package which contains the version file
    """
    if not Path(version_file_path).exists():
        raise click.ClickException(f"Version file not found: {version_file_path}")

    path_to_package = Path(version_file_path).parent
    package_name = path_to_package.name
    version_file_name = Path(version_file_path).name

    return package_name, path_to_package, version_file_name


def validate_version_file(version_file):
    if version_file == "" or version_file == {}:
        raise click.ClickException(
            "Empty version file path in pyproject.toml. " "Please provide a valid path"
        )


# TODO: we need to remove this function
def find_package_and_version_file(project_root="."):
    version_file_name = "__init__.py"
    package_name, path_to_package = find_package_in_src(project_root)

    return package_name, path_to_package, version_file_name
