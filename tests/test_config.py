import toml
import yaml

from pkgmt import config


def test_load_toml(tmp_empty):
    cfg_ = {"github": "edublancas/pkgmt"}
    cfg = {"tool": {"pkgmt": cfg_}}

    with open("pyproject.toml", "w") as f:
        toml.dump(cfg, f)

    loaded = config.load()

    assert loaded == cfg_


def test_load_yaml(tmp_empty):
    cfg_ = {"github": "edublancas/pkgmt"}
    cfg = {"pkgmt": cfg_}

    with open("config.yaml", "w") as f:
        yaml.dump(cfg, f)

    loaded = config.load()

    assert loaded == cfg_
