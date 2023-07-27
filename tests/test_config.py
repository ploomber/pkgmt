import toml
import pytest

from pkgmt import config


@pytest.fixture
def toml_cfg(tmp_empty):
    cfg_ = {"github": "edublancas/pkgmt", "version": {"tag": True, "push": True}}
    cfg = {"tool": {"pkgmt": cfg_}}

    with open("pyproject.toml", "w") as f:
        toml.dump(cfg, f)

    yield cfg_


def test_load_toml(toml_cfg):
    loaded = config.Config.from_file("pyproject.toml")

    assert loaded == toml_cfg


def test_missing_file(tmp_empty):
    with pytest.raises(FileNotFoundError) as excinfo:
        config.Config.from_file("pyproject.toml")
    assert "Could not load configuration file: expected a pyproject.toml file" in str(
        excinfo.value
    )


def test_key_error(toml_cfg):
    cfg = config.Config.from_file("pyproject.toml")

    with pytest.raises(KeyError) as excinfo:
        cfg["some_key"]

    assert "doesn't have key" in str(excinfo.value)
