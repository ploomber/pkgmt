import os
from pathlib import Path
from pkgmt.versioner.abstractversioner import AbstractVersioner


class VersionerNonSetup(AbstractVersioner):

    def __init__(self, version_package, project_root='.'):
        self.version_package = version_package
        super().__init__(project_root)

    def find_package(self):

        for path, dirs, files in os.walk(self.project_root):
            if self.version_package in dirs:
                PACKAGE = Path(path, self.version_package)

        package_name = self.version_package
        return package_name, PACKAGE

    def version_file(self):
        return '_version.py'
