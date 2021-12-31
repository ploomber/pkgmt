from pathlib import Path
from glob import iglob
import re
from collections import namedtuple, defaultdict
from itertools import chain
import requests

Response = namedtuple('Response', ['url', 'code', 'broken'])


def _make_glob_exp(extension):
    return f'**/*.{extension}'


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

    broken = defaultdict(lambda: [])
    globs = (iglob(_make_glob_exp(ext), recursive=True) for ext in extensions)

    for file in chain(*globs):
        text = Path(file).read_text()
        broken[file].extend(
            find_broken_in_text(text, ignore_substrings=ignore_substrings))

    out = {file: urls for file, urls in broken.items() if urls}

    if verbose:
        for file, broken in out.items():
            if broken:
                print(f'*** {file} ***')
                print('\n'.join(broken))

    return out


def find_broken_in_text(text, ignore_substrings=None):
    """Find broken links
    """
    links = _find(text, ignore_substrings=ignore_substrings)
    responses = [_check_if_broken(link) for link in links]
    return [res.url for res in responses if res.broken]


def _find(text, ignore_substrings=None):
    """Find links in text
    """
    ignore_substrings = ignore_substrings or []
    # source: https://www.geeksforgeeks.org/python-check-url-string/
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"  # noqa
    url = re.findall(regex, text)

    return [
        x[0] for x in url
        if not any(substr in x[0] for substr in ignore_substrings)
    ]


def _check_if_broken(url):
    """Check if a link is broken
    """
    try:
        res = requests.get(url)
        code = res.status_code
        broken = not res.ok
    except requests.exceptions.ConnectionError:
        code = None
        broken = True
    except requests.exceptions.MissingSchema:
        code = None
        broken = True

    response = Response(url, code, broken)

    return response
