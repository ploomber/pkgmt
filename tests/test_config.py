import toml
import pytest

from pkgmt import config
from pkgmt.exceptions import InvalidConfiguration


@pytest.fixture
def toml_cfg(tmp_empty):
    cfg_ = {"github": "edublancas/pkgmt", "version": {"tag": True, "push": True}}
    cfg = {"tool": {"pkgmt": cfg_}}

    with open("pyproject.toml", "w") as f:
        toml.dump(cfg, f)

    yield cfg_


@pytest.mark.parametrize(
    "data",
    [
        {
            "tool": {
                "pkgmt": {
                    "github": "edublancas/pkgmt",
                    "version": {"tag": True, "push": True},
                }
            }
        },
        {
            "tool": {
                "pkgmt": {
                    "github": "edublancas/pkgmt",
                    "version": {"tag": True, "push": True},
                    "env_name": "jupysql",
                    "package_name": "sql",
                }
            }
        },
    ],
)
def test_load_toml(data, tmp_empty):
    with open("pyproject.toml", "w") as f:
        toml.dump(data, f)

    loaded = config.Config.from_file("pyproject.toml")

    assert loaded == data["tool"]["pkgmt"]


def test_missing_file(tmp_empty):
    with pytest.raises(FileNotFoundError) as excinfo:
        config.Config.from_file("pyproject.toml")
    assert "Could not find configuration file: expected a pyproject.toml file" in str(
        excinfo.value
    )


def test_key_error(toml_cfg):
    cfg = config.Config.from_file("pyproject.toml")

    with pytest.raises(KeyError) as excinfo:
        cfg["some_key"]

    assert "doesn't have key" in str(excinfo.value)


@pytest.mark.parametrize(
    "cfg, error",
    [
        [
            {"somekey": {"pkgmt": {"github": "edublancas/pkgmt"}}},
            "Missing key : 'tool'.\npyproject.toml should contain " "'tool.pkgmt' key",
        ],
        [
            {"tool": {"somekey": {"github": "edublancas/pkgmt"}}},
            "Missing key : 'pkgmt'.\npyproject.toml should contain " "'tool.pkgmt' key",
        ],
    ],
)
def test_pkgmt_key_missing(tmp_empty, cfg, error):
    with open("pyproject.toml", "w") as f:
        toml.dump(cfg, f)
    with pytest.raises(InvalidConfiguration) as excinfo:
        config.Config.from_file("pyproject.toml")
    assert error in str(excinfo.value)
