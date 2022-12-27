import json
import subprocess
import concurrent.futures
from pathlib import Path
from glob import iglob
import re
from itertools import chain
import requests


class Response:
    def __init__(self, url, code, broken) -> None:
        self.url = url
        self.code = code
        self.broken = broken

    def __hash__(self) -> int:
        return hash(self.url)

    def __eq__(self, another) -> bool:
        return self.url == another

    def __repr__(self) -> str:
        return f"({self.code}) {self.url}"


def _make_glob_exp(extension):
    return f"**/*.{extension}"


def _find_match(links, broken):
    result = []

    for link in links:
        if link in broken:
            result.append(broken[link])

    return result


def _read_file(file):
    file = Path(file)

    if file.suffix == ".ipynb":
        # we need to load the notebook's content; otherwise special characters
        # are not resolved correctly since they're double escaped in the
        # JSON file. Also, notebooks are always encoded as UTF-8
        nb = json.loads(file.read_text(encoding="utf-8"))
        return "\n".join(["\n".join(cell["source"]) for cell in nb["cells"]])
    else:
        return file.read_text()


def find_broken_in_files(extensions, ignore_substrings=None, verbose=False):
    """
    Parameters
    ----------
    find_broken_in_files : str or list
        File extensions to check. Can be a str ("md") or a list such as
        ["md", "rst"]
    """
    if isinstance(extensions, str):
        extensions = [extensions]

    mapping = _find_links_in_files(extensions, ignore_substrings=ignore_substrings)

    broken = {response.url: response for response in _find_broken_links(mapping)}

    if verbose:
        for file, links in mapping.items():
            match = _find_match(links, broken)

            if match:
                print(f"*** {file} ***")
                print("\n".join([repr(m) for m in match]))

    return broken


def _find_links_in_files(extensions, ignore_substrings=None):
    globs = (iglob(_make_glob_exp(ext), recursive=True) for ext in extensions)
    content = dict()

    tracked_by_git, error = _git_tracked_files()

    for file in chain(*globs):
        if error or file in tracked_by_git:
            text = _read_file(file)
            content[file] = _find(text, ignore_substrings=ignore_substrings)

    return content


def _find_broken_links(mapping):
    urls = [item for sublist in mapping.values() for item in sublist]

    broken = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_url = {executor.submit(_check_if_broken, url): url for url in urls}

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                response = future.result()
            except Exception as exc:
                print("%r generated an exception: %s" % (url, exc))
            else:

                if response.broken:
                    broken.append(response)

    return broken


def _find(text, ignore_substrings=None):
    """Find links in text"""
    ignore_substrings = ignore_substrings or []
    # source: https://www.geeksforgeeks.org/python-check-url-string/
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"  # noqa
    url = re.findall(regex, text)

    return [
        x[0] for x in url if not any(substr in x[0] for substr in ignore_substrings)
    ]


def _check_if_broken(url):
    """Check if a link is broken"""
    try:
        res = requests.head(url)
        code = res.status_code
        broken = not res.ok
    except requests.exceptions.ConnectionError:
        code = None
        broken = True
    except requests.exceptions.MissingSchema:
        code = None
        broken = True

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/405
    if code == 405:
        broken = False

    response = Response(url, code, broken)

    return response


# copied from soopervisor
def _git_tracked_files():
    """
    Returns
    -------
    list or None
        List of tracked files or None if an error happened
    None of str
        None if successfully retrieved tracked files, str if an error happened
    """
    res = subprocess.run(
        ["git", "ls-tree", "-r", "HEAD", "--name-only"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if not res.returncode:
        return set(res.stdout.decode().splitlines()), None
    else:
        return None, res.stderr.decode().strip()
