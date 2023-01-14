import re


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
