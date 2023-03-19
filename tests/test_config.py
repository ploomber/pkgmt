import toml
import yaml
import pytest

from pkgmt import config


@pytest.fixture
def toml_cfg(tmp_empty):
    cfg_ = {"github": "edublancas/pkgmt"}
    cfg = {"tool": {"pkgmt": cfg_}}

    with open("pyproject.toml", "w") as f:
        toml.dump(cfg, f)

    yield cfg_


def test_load_toml(toml_cfg):
    loaded = config.load()

    assert loaded == toml_cfg


def test_load_yaml(tmp_empty):
    cfg_ = {"github": "edublancas/pkgmt"}
    cfg = {"pkgmt": cfg_}

    with open("config.yaml", "w") as f:
        yaml.dump(cfg, f)

    loaded = config.load()

    assert loaded == cfg_


def test_missing_file(tmp_empty):
    with pytest.raises(FileNotFoundError):
        config.load()


def test_key_error(toml_cfg):
    cfg = config.load()

    with pytest.raises(KeyError) as excinfo:
        cfg["some_key"]

    assert "doesn't have key" in str(excinfo.value)
