import pytest

from pkgmt.versioner.util import (
    _split_prerelease_part,
    complete_version_string,
    is_major_version,
)


@pytest.mark.parametrize(
    "version, version_part, prerelease_part",
    [
        ["1", "1", ""],
        ["0.1", "0.1", ""],
        ["2.1.3", "2.1.3", ""],
        ["1a1", "1", "a1"],
        ["1.0b10", "1.0", "b10"],
        ["2.5.4rc2", "2.5.4", "rc2"],
    ],
)
def test_split_prerelease_part(version, version_part, prerelease_part):
    assert _split_prerelease_part(version) == (version_part, prerelease_part)


@pytest.mark.parametrize(
    "version, expected",
    [
        ["1", "1.0.0"],
        ["0.1", "0.1.0"],
        ["2.1.3", "2.1.3"],
        ["1a1", "1.0.0a1"],
        ["1.0b10", "1.0.0b10"],
        ["2.5.4rc2", "2.5.4rc2"],
    ],
)
def test_complete_version_string(version, expected):
    assert complete_version_string(version) == expected


@pytest.mark.parametrize(
    "version, expected",
    [
        ["0.2dev", True],
        ["0.3.0dev", True],
        ["4.0.0dev", True],
        ["4.1.0dev", True],
        ["2.0dev", True],
        ["2.5dev", True],
        ["5dev", True],
        ["0.0.1dev", False],
        ["0.1.1dev", False],
        ["1.2.3dev", False],
    ],
)
def test_is_major_version(version, expected):
    assert is_major_version(version) is expected
