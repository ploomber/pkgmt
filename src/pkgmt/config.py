from collections.abc import Mapping

import toml
import click
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

    @staticmethod
    def _validate_config(data):
        """
        Function to validate top level and version keys in
        config file.
        """

        top_level_keys = list(data)
        invalid_top_level_keys = [
            key for key in top_level_keys if key not in VALID_KEYS
        ]
        if invalid_top_level_keys:
            raise InvalidConfiguration(
                f"Invalid keys in pyproject.toml file: "
                f"{', '.join(invalid_top_level_keys)}. "
                f"Valid keys are: {', '.join(VALID_KEYS)}"
            )

        version_data = data.get("version", {})
        version_keys = list(version_data)

        invalid_version_keys = [
            key for key in version_keys if key not in VALID_VERSION_KEYS
        ]
        if invalid_version_keys:
            raise InvalidConfiguration(
                f"Invalid version keys in pyproject.toml "
                f"file: {', '.join(invalid_version_keys)}. "
                f"Valid version keys are: {', '.join(VALID_VERSION_KEYS)}"
            )

    @staticmethod
    def _validate_boolean_key(keys, values):
        if not isinstance(keys, list):
            keys = [keys]
        if not isinstance(values, list):
            values = [values]

        if len(keys) != len(values):
            raise ValueError("Keys and values lists must have the same length")

        invalid_keys = [
            key
            for key, value in zip(keys, values)
            if value is not None and not isinstance(value, bool)
        ]

        if invalid_keys:
            raise InvalidConfiguration(
                f"Invalid values for keys: "
                f"{', '.join(invalid_keys)}. Expected booleans."
            )

    @staticmethod
    def _resolve_cli_config_settings(setting_name, cli_setting, cfg_setting):
        if cli_setting is not None:
            if cfg_setting is not None and cli_setting != cfg_setting:
                click.echo(
                    f"Value of '{setting_name}' from CLI : {cli_setting}. "
                    f"This will override push={cfg_setting} "
                    f"as configured in pyproject.toml"
                )
            return cli_setting
        return cfg_setting if cfg_setting is not None else True

    @staticmethod
    def _generate_overriding_error(key, cli_value, cfg_value):
        return (
            f"Value of '{key}' from CLI: {cli_value}. This will override "
            f"{key}={cfg_value} as configured in pyproject.toml"
        )

    @staticmethod
    def _resolve_version_configuration(data, cli_args):
        """
        Function to return tag and push from
        pyproject.toml if provided by user.
        Example file:
        [tool.pkgmt]
        github = "repository/package"
        version = {version_file = "/app/_version.py", tag=True, push=False}
        """

        if cli_args is None:
            cli_args = {}

        cfg_version = data.get("version", {})
        cfg_tag = cfg_version.get("tag", None)
        cfg_push = cfg_version.get("push", None)

        tag = cli_args.get("tag") if cli_args.get("tag") is not None else cfg_tag
        push = cli_args.get("push") if cli_args.get("push") is not None else cfg_push

        keys_to_validate = ["tag", "push"]
        values_to_validate = [tag, push]

        Config._validate_boolean_key(keys_to_validate, values_to_validate)

        conflicts = []
        if cfg_tag is not None and tag != cfg_tag:
            conflicts.append(Config._generate_overriding_error("tag", tag, cfg_tag))
        if cfg_push is not None and push != cfg_push:
            conflicts.append(Config._generate_overriding_error("push", push, cfg_push))

        if conflicts:
            click.echo("\n".join(conflicts))

        tag = tag if tag is not None else True
        push = push if push is not None else True

        version = {"tag": tag, "push": push}
        data.setdefault("version", {}).update(version)
        return data

    @classmethod
    def from_file(cls, file, **kwargs):
        if Path(file).exists():
            try:
                with open(file) as f:
                    data = toml.load(f)["tool"]["pkgmt"]
                    Config._validate_config(data)
                    data = Config._resolve_version_configuration(
                        data, kwargs.get("cli_args")
                    )
                    return cls(data, "pyproject.toml")
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
