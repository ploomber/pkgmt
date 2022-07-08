import toml
import yaml
from pathlib import Path


def load():
    if Path('pyproject.toml').exists():
        with open('pyproject.toml') as f:
            return toml.load(f)['tool']['pkgmt']
    elif Path('config.yaml').exists():
        with open("config.yaml", "r") as stream:
            try:
                return yaml.safe_load(stream)['pkgmt']
            except yaml.YAMLError as exc:
                print("Error loading config.yaml file : {}".format(exc))
