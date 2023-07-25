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


class PyprojectConfig:
    def __init__(self):
        self.cfg = None
        if Path("pyproject.toml").exists():
            try:
                with open("pyproject.toml") as f:
                    self.cfg = Config(toml.load(f)["tool"]["pkgmt"], "pyproject.toml")
                    self.validate_config()
            except toml.decoder.TomlDecodeError as e:
                raise InvalidConfiguration(
                    f"Invalid pyproject.toml file: {str(e)}."
                    "If using a boolean "
                    "value ensure it's in lowercase, e.g., key = true"
                ) from e
        else:
            raise FileNotFoundError(
                "Could not load configuration file: expected a pyproject.toml file"
            )

    def get_config(self):
        return self.cfg

    def validate_config(self):
        """
        Function to validate top level and version keys in
        config file.
        """
        keys = list(self.cfg.keys())
        for key in keys:
            if key not in VALID_KEYS:
                raise InvalidConfiguration(
                    f"Invalid key '{key}' in"
                    f" pyproject.toml file. Valid keys are : "
                    f"{', '.join(VALID_KEYS)}"
                )

            if self.cfg.get("version", {}):
                version_keys = list(self.cfg.get("version").keys())
                for key in version_keys:
                    if key not in VALID_VERSION_KEYS:
                        raise InvalidConfiguration(
                            f"Invalid version key '{key}' in"
                            f" pyproject.toml file. Valid keys are : "
                            f"{', '.join(VALID_VERSION_KEYS)}"
                        )

    def get_version_configurations(self):
        """
        Function to return tag and push from
        pyproject.toml if provided by user.
        Example file:
        [tool.pkgmt]
        github = "repository/package"
        version = {version_file = "/app/_version.py", tag=True, push=False}
        """
        tag = self.cfg.get("version", {}).get("tag", None)
        push = self.cfg.get("version", {}).get("push", None)
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
