import toml

from pkgmt import config


def test_load(tmp_empty):
    cfg_ = {'github': 'edublancas/pkgmt'}
    cfg = {'tool': {'pkgmt': cfg_}}

    with open('pyproject.toml', 'w') as f:
        toml.dump(cfg, f)

    loaded = config.load()

    assert loaded == cfg_
