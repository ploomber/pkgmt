import os
import warnings
from pathlib import Path
from pkgmt.versioner.abstractversioner import AbstractVersioner


class VersionerSetup(AbstractVersioner):
    def find_package(self):
        path_to_src = Path(self.project_root, "src")

        if not path_to_src.is_dir():
            raise NotADirectoryError(
                f"Expected a directory at {str(path_to_src)!r} but it doesn't exist"
            )

        dirs = sorted(
            [
                f
                for f in os.listdir(path_to_src)
                if Path("src", f).is_dir()
                and not f.endswith(".egg-info")
                and Path(f).name != "__pycache__"
            ]
        )

        if len(dirs) != 1:
            warnings.warn(
                "Found more than one dir, " f"choosing the first one: {dirs[0]}"
            )

        package_name = dirs[0]
        PACKAGE = path_to_src / package_name
        return package_name, PACKAGE

    def version_file(self):
        return "__init__.py"
