from collections.abc import Mapping

import toml
import yaml
from pathlib import Path


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


def load():
    if Path("pyproject.toml").exists():
        with open("pyproject.toml") as f:
            return Config(toml.load(f)["tool"]["pkgmt"], "pyproject.toml")
    elif Path("config.yaml").exists():
        with open("config.yaml", "r") as stream:
            try:
                return Config(yaml.safe_load(stream)["pkgmt"], "config.yaml")
            except yaml.YAMLError as exc:
                print("Error loading config.yaml file : {}".format(exc))
    else:
        raise FileNotFoundError(
            "Could not load config: expected pyproject.toml or config.yaml"
        )
