from collections.abc import Mapping

import toml
from pathlib import Path
from pkgmt.exceptions import InvalidConfiguration

VALID_KEYS = ["github", "version", "package_name", "check_links"]
VALID_VERSION_KEYS = ["version_file", "tag", "push"]


class Config(Mapping):
    def __init__(self, data, name) -> None:
        self._data = data
        self._name = name

    def __getitem__(self, key):
        if key not in self._data:
            raise KeyError(f"Configuration {self._data!r} doesn't have key: {key!r}")

        return self._data[key]

    def __iter__(self):
        for key in self._data:
            yield key

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._data!r})"


def validate_config(cfg):
    """
    Function to validate top level and version keys in
    config file.
    """
    keys = list(cfg.keys())
    for key in keys:
        if key not in VALID_KEYS:
            raise InvalidConfiguration(
                f"Invalid key '{key}' in"
                f" pyproject.toml file. Valid keys are : "
                f"{', '.join(VALID_KEYS)}"
            )

        if cfg.get("version", {}):
            version_keys = list(cfg.get("version").keys())
            for key in version_keys:
                if key not in VALID_VERSION_KEYS:
                    raise InvalidConfiguration(
                        f"Invalid version key '{key}' in"
                        f" pyproject.toml file. Valid keys are : "
                        f"{', '.join(VALID_VERSION_KEYS)}"
                    )


def read_version_configurations(cfg):
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
        raise InvalidConfiguration(
            "Type of 'tag' key in pyproject.toml is invalid. "
            "It should be lowercase boolean : true / false"
        )
    if push is not None and not isinstance(push, bool):
        raise InvalidConfiguration(
            "Type of 'push' key in pyproject.toml is invalid. "
            "It should be lowercase boolean : true / false"
        )
    return tag, push


def load():
    if Path("pyproject.toml").exists():
        try:
            with open("pyproject.toml") as f:
                cfg = Config(toml.load(f)["tool"]["pkgmt"], "pyproject.toml")
                validate_config(cfg)
                return cfg
        except toml.decoder.TomlDecodeError as e:
            raise InvalidConfiguration(
                f"Invalid pyproject.toml file: {str(e)}."
                "If using a boolean "
                "value ensure it's in lowercase, e.g., key = true"
            )
    else:
        raise FileNotFoundError(
            "Could not load configuration file: expected a pyproject.toml file"
        )
