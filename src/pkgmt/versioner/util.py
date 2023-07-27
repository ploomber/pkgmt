import re
import os
import click
import warnings
from pathlib import Path
from pkgmt.config import Config


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
    Function to find the path of the package inside src directory

    Parameters
    ----------
    project_root: str, root folder of the project.
                  Default is "."

    Returns
    -------
    name and path of package inside src. If multiple packages found,
    first is selected
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
    PACKAGE = path_to_src / package_name
    return package_name, PACKAGE


def find_package_of_version_file(version_file_path, project_root="."):
    """
    Function to find the path of the package inside src directory

    Parameters
    ----------

    version_file_path: str, path of the file in which
                       __version__ string is stored

    project_root: str, root folder of the project.
                  Default is "."

    Returns
    -------
    name and path of package which contains the version file
    """

    PACKAGE = None
    try:
        version_file_name = os.path.basename(version_file_path)
        version_package = os.path.basename(os.path.dirname(version_file_path))
    except TypeError:
        raise click.ClickException(
            f"Invalid path : {version_file_path}. "
            f"Please provide a valid path for the version file"
        )
    for path, dirs, _ in os.walk(project_root):
        if version_package in dirs:
            PACKAGE = Path(path, version_package)
            if not Path(path, version_package, version_file_name).exists():
                raise click.ClickException(
                    f"Cannot find version file {version_file_path} "
                    f"in subdirectory : {version_package}"
                )

    if PACKAGE is None:
        raise click.ClickException(
            f"Version file path does not exist : {version_file_path}"
        )
    package_name = version_package
    return package_name, PACKAGE, version_file_name


def validate_version_file(version_file):
    if version_file == "" or version_file == {}:
        raise click.ClickException(
            "Empty version file path in pyproject.toml. " "Please provide a valid path"
        )


def find_package_and_version_file(project_root="."):
    """
    Function to find the path of the package containing the
    version file. If version_file key is found in pyproject.toml
    file, this path is considered as the path to the version file.
    Else version file in __init__.py found in the first package
    inside src directory.
    """
    cfg = Config.from_file("pyproject.toml")
    version_file = cfg.get("version", {}).get("version_file", None)
    validate_version_file(version_file)
    if version_file:
        package_name, PACKAGE, version_file_name = find_package_of_version_file(
            version_file, project_root
        )
    else:
        version_file_name = "__init__.py"
        package_name, PACKAGE = find_package_in_src(project_root)
    return package_name, PACKAGE, version_file_name
