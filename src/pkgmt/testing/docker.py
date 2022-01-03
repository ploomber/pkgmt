"""
Testing rst files that call "docker run"
"""
from pathlib import Path

from pkgmt.testing import rst

_template = """\
# exit on error and print each command
set -e
set -x
ROOT=$(pwd)

{code}\
"""


# NOTE: should I modify the command to have the --rm flag?
def _find_docker_run_idx(snippets):
    for i, snippet in enumerate(snippets):
        if 'docker run' in snippet:
            return i

    raise ValueError('Did not find "docker run" command')


def _patch_docker_run(snippet):
    lines = snippet.splitlines()
    idx = None

    for i, line in enumerate(lines):
        if line.startswith('docker run'):
            idx = i

    if idx is None:
        raise ValueError('Failed to find a line starting with '
                         f'"docker run", got lines: {lines}')

    docker_run_line = lines[idx]

    if '-t' not in docker_run_line:
        raise ValueError('Expected -t flag to be in the "docker run"'
                         f' command, got: {docker_run_line!r}')

    # cd to $ROOT because the script may have some "cd" commands, and
    # we're saving run-in-docker.sh in the initial working directory
    lines[idx] = ('cd $ROOT && cat run-in-docker.sh | ' +
                  docker_run_line.replace('-t ', ''))

    return '\n'.join(lines)


def to_script(text):
    snippets = rst.to_snippets(text)

    idx = _find_docker_run_idx(snippets)

    pre, post = snippets[:idx + 1], snippets[idx + 1:]

    return pre, post


def to_testing_files(text):
    pre, post = to_script(text)
    pre[-1] = _patch_docker_run(pre[-1])

    Path('test.sh').write_text(_template.format(code='\n\n'.join(pre)))
    Path('run-in-docker.sh').write_text(
        _template.format(code='\n\n'.join(post)))


def to_testing_files_from_path(path):
    to_testing_files(Path(path).read_text())
