from pathlib import Path
import re
from glob import iglob
from collections import defaultdict

import click

from pkgmt.versioner.util import complete_version_string
from pkgmt.exceptions import ProjectValidationError
from pkgmt.versioner.versioner import Versioner


class Deprecations:
    def __init__(self, root_dir=None) -> None:
        self.root_dir = root_dir

        versioner = Versioner(project_root=root_dir)
        self.current = complete_version_string(
            versioner.current_version().replace("dev", "")
        )

    def check(self):
        """Check if there are pending deprecations"""
        deprecations = find_deprecations(root_dir=self.root_dir)

        mapping = defaultdict(lambda: [])

        for dep in deprecations:
            mapping[complete_version_string(dep.version)].append(dep)

        if self.current in mapping:
            matches_out = "\n".join(f"- {item}" for item in mapping[self.current])
            raise ProjectValidationError(
                f"Found the following pending deprecations:\n{matches_out}"
            )


class DeprecationItem:
    def __init__(self, body, version, path) -> None:
        self.body = body
        self.version = version
        self.path = str(Path(path))

    def __eq__(self, o: object) -> bool:
        return (
            self.body == o.body
            and self.version == o.version
            and Path(self.path) == Path(o.path)
        )

    def __hash__(self) -> int:
        return hash((self.body, self.version, self.path))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.body!r}, {self.version!r}, {self.path!r})"

    def __str__(self) -> str:
        return f"{self.body!r} at {self.path!r}"


def _find_deprecations_in_text(text):
    """Find and parse `.. deprecated::` directives in text

    Returns
    -------
    bodies : list
        Content of each `.. deprecated::` directive

    versions : list
        Versions parsed from the body of each directive
    """
    # .. deprecated:: {version} [whitespace]
    # [word chars or space] [version descriptor] [word chars or space]
    bodies = re.findall(
        r"\.\. deprecated::\s+[0-9\.]+\s+([\w,.` \n\-]+\ +[0-9\.]+[\w,`. \n\-]*\n{1})",
        text,
    )

    versions = [re.search(r"[0-9\.]{3,5}", body).group() for body in bodies]

    return bodies, versions


def find_deprecations(root_dir=None):
    deprecations = []

    root_dir = root_dir or "."

    for path in iglob(f"{root_dir}/**/*.py", recursive=True):
        try:
            bodies, version = _find_deprecations_in_text(Path(path).read_text())
        except Exception:
            print(f"Issue reading file: {path}")
            raise

        for body, version in zip(bodies, version):
            deprecations.append(DeprecationItem(body, version, path))

    return deprecations


@click.command()
@click.argument("root")
def _cli(root):
    Deprecations(root).check()


if __name__ == "__main__":
    _cli()
