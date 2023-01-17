"""
Check which dependencies were updated most recently
"""

import concurrent.futures
from functools import total_ordering

import click
import requests
from pip._internal.operations import freeze


def get_latest_version(package_name):
    """Check the latest available version"""
    res = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    return res.json()


@total_ordering
class Package:
    def __init__(self, name) -> None:
        self.name = name
        self.last_version = None
        self.last_updated = None

    def fetch(self):
        response = get_latest_version(self.name)

        self.last_version = response["info"]["version"]

        # this returns one for wheel, one for source, and possibly
        # others for yanked versions (?), we use the most recent one
        self.last_updated = max(
            [r["upload_time_iso_8601"] for r in response["releases"][self.last_version]]
        )

    def __repr__(self) -> str:
        repr_ = f"{type(self).__name__}({self.name!r})"

        if self.last_updated:
            repr_ = f"{repr_} @ {self.last_updated}"

        return repr_

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.last_updated < other.last_updated


def main():
    pkgs = [Package(dep.split("==")[0]) for dep in freeze.freeze()]

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future2pkg = {executor.submit(pkg.fetch): pkg for pkg in pkgs}

        for future in concurrent.futures.as_completed(future2pkg):
            try:
                future.result()
            except Exception as e:
                pkg = future2pkg[future]
                print(f"{pkg} generated an exception: {e}")

    pkgs_valid = sorted([pkg for pkg in pkgs if pkg.last_updated is not None])

    pkgs_valid_ = "\n".join(repr(pkg) for pkg in pkgs_valid)

    pkgs_invalid = "\n".join([repr(pkg) for pkg in pkgs if pkg.last_updated is None])

    click.echo(f"Invalid packages: {pkgs_invalid}")
    click.echo(f"Valid packages (recently updated first): {pkgs_valid_}")


@click.command()
def _cli():
    """Retrieve latest updated packages in the current environment"""
    main()


if __name__ == "__main__":
    _cli()
