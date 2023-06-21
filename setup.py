import io
import re
import ast
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext

from setuptools import find_packages
from setuptools import setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with open("src/pkgmt/__init__.py", "rb") as f:
    VERSION = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


REQUIRES = [
    # core dependencies
    "toml",
    "pyyaml",
    "requests",
    "click",
    "invoke",
    # dependencies for linting and formatting
    "black",
    "nbqa",
    "flake8",
    "jupytext",
    # ensure we have a valid IPython version since
    # black needs it
    "ipython<=8.12.0; python_version <= '3.8'",
    "ipython",
]


DEV = [
    "pytest",
    "twine",
    # optional dependency for test module
    "jupytext",
    "nbclient",
    "ipykernel",
]

# to test markdown files
ALL = [
    "nbclient",
    "jupytext",
    "ipykernel",
]

# to run: pkgmt check
CHECK = [
    # for check-project
    "mistune>=3rc",
]

setup(
    name="pkgmt",
    version=VERSION,
    description=None,
    license=None,
    author=None,
    author_email=None,
    url=None,
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: MIT License",
    ],
    keywords=[],
    install_requires=REQUIRES,
    extras_require={
        "dev": DEV + CHECK,
        "all": ALL,
        "check": CHECK,
    },
    entry_points={
        "console_scripts": ["pkgmt=pkgmt.cli:cli"],
    },
)
