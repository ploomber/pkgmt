import toml


def load():
    with open('pyproject.toml') as f:
        return toml.load(f)['tool']['pkgmt']
