# regex taken from inducer/pudb's detect_encoding
import re
pythonEncodingDirectiveRE = re.compile("^\s*#.*coding[:=]\s*([-\w.]+)")

def detect_encoding(source):
    """
    Given some python contents as a byte string, return the name of the encoding, or else None.
    """
    # According to the PEP0263, the encoding directive must appear on one of the first two lines of the file
    top_lines = source.split('\n', 2)[:2]

    for line in top_lines:
        encodingMatch = pythonEncodingDirectiveRE.search(line)
        if encodingMatch:
            return encodingMatch.group(1)

    # We didn't find anything.
    return None

def parse(python_contents, encoding):
    """
    Given some python contents as a unicode string, return the lxml representation.
    """
    import ast
    ast_python = ast.parse(python_contents)
    dictnode_python = ast_to_dictnode(ast_python)
    return dictnode_python

    from refactorlib.parse import dictnode_to_lxml
    return dictnode_to_lxml(dictnode_python, encoding=encoding)


def iter_fields(node):
    """
    Yield a tuple of ``(fieldname, value)`` for each field in ``node._fields``
    that is present on *node*.
    """
    for field in node._fields:
        try:
            yield field, getattr(node, field)
        except AttributeError:
            pass


def ast_to_dictnode(ast):
    """
    Transform a ast structure into a dictnode, as defined by dictnode_to_lxml.
    """
    from _ast import AST
    #from refactorlib.dictnode import DictNode
    DictNode = dict
    root_nodelist = []

    stack = [(root_nodelist, [ast])]

    while stack:
        nodelist, nodes = stack.pop()
        for node in nodes:
            if not isinstance(node, AST):
                raise ValueError("%s: %r" % (type(node).__name__, node))

            dictnode = DictNode(name=type(node).__name__)
            dictnode['children'] = children = []
            dictnode['attrs'] = attrs = {}
            for field, val in iter_fields(node):
                if field in ('name', 'attrs', 'children'):
                    raise ValueError("%s: %r" % (field, val))
                if type(val) is list and all(isinstance(node, AST) for node in val):
                    childlist = []
                    children.append(
                        DictNode(name=field, children=childlist)
                    )
                    stack.append((childlist, val))
                elif isinstance(val, AST):
                    childlist = []
                    children.append(DictNode(name=field, children=childlist))
                    stack.append((childlist, [val]))
                elif type(val) in (int, str):
                    attrs[field] = val
                else:
                    raise ValueError("%s: %r" % (field, val))

            if node._attributes:
                for attr in node._attributes:
                    val = getattr(node, attr)
                    if type(val) in (int, str):
                        attrs[attr] = val
                    else:
                        raise ValueError("%s: %r" % (attr, val))

            for key in dictnode.keys():
                if not dictnode[key]:
                    del dictnode[key]

            nodelist.append(dictnode)

    if not isinstance(ast, AST):
        raise TypeError('expected AST, got %r' % type(ast).__name__)

    assert len(root_nodelist) == 1, root_nodelist
    return root_nodelist[0]
