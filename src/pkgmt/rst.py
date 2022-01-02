"""
Utilities for executing .rst files

Resources:

http://www.xavierdupre.fr/blog/2015-06-07_nojs.html
https://www.bustawin.com/sphinx-extension-devel/
https://docutils.sourceforge.io/docs/howto/rst-directives.html
https://github.com/sphinx-doc/sphinx/blob/fe47bf46cbb6a615b01d6c5dc9fdcac58c940f69/sphinx/parsers.py
"""
from pathlib import Path

from docutils.parsers.rst import Parser
from docutils.utils import new_document
from docutils import nodes

# from sphinx.parsers import RSTParser
from docutils.parsers.rst import directives
from sphinx.directives.code import CodeBlock

_parser = Parser()
# TODO: we should use Sphinx's RSTParser, otherwise some files will
# break if they use sphinx-exclusive directives
# _parser = RSTParser()

directives.register_directive('code-block', CodeBlock)

_template = """\
# exit on error and print each command
set -e
set -x

{code}\
"""


def parse_from_path(path):
    return parse(Path(path).read_text())


def parse(content):
    # maybe use sphinx's parser - it should be configured with the custom
    # directives
    doc = new_document('doc.rst')
    doc.settings.pep_references = None
    doc.settings.rfc_references = None
    # doc.settings.tab_width = None

    _parser.parse(content, doc)

    elements = doc.traverse()

    selected = []

    for e in elements:
        if (isinstance(e, nodes.literal_block) and
                e.attributes.get('language') in {'sh', 'bash'}) or isinstance(
                    e, (nodes.container, nodes.comment)):
            selected.append(e)

    def previous_not_comment(idx, elements):
        if idx == 0:
            return False
        else:
            prev = elements[idx - 1]

            if not isinstance(prev, nodes.comment):
                return False

            return prev.astext() == 'skip-next'

    snippets = [
        s for i, s in enumerate(selected)
        if not previous_not_comment(i, selected)
        and not isinstance(s, nodes.comment)
    ]

    code_user = '\n\n'.join(s.astext() for s in snippets)
    code_script = _template.format(code=code_user)

    return code_script
