# -*- coding: UTF-8 -*-
import re


# regex taken from inducer/pudb's detect_encoding
pythonEncodingDirectiveRE = re.compile(r"^\s*#.*coding[:=]\s*([-\w.]+)")


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
    lib2to3_python = lib2to3_parse(python_contents)
    dictnode_python = lib2to3_to_dictnode(lib2to3_python)

    from refactorlib.parse import dictnode_to_lxml
    return dictnode_to_lxml(dictnode_python, encoding=encoding)


def lib2to3_parse(python_contents):
    from lib2to3 import pygram, pytree
    from lib2to3.pgen2 import driver

    drv = driver.Driver(pygram.python_grammar, pytree.convert)
    tree = drv.parse_string(python_contents, True)
    return tree


def lib2to3_to_dictnode(tree):
    """
    Transform a lib2to3 structure into a dictnode, as defined by dictnode_to_lxml.
    """
    from lib2to3.pygram import python_grammar
    from lib2to3.pgen2.token import tok_name

    code2name = tok_name.copy()
    del code2name[256]
    code2name.update(python_grammar.number2symbol)

    root = dict(name='ROOT', children=[], attrs={})
    stack = [(tree, root)]
    prev_node = root

    while stack:
        node, parent = stack.pop()
        node_type = code2name.get(node.type, node.type)
        attrs = {}

        if hasattr(node, 'value'):
            node_text = node.value
        else:
            node_text = ''

        if hasattr(node, '_prefix') and node._prefix:
            if prev_node is parent:
                if parent is root:
                    assert node_text == '', node_text
                    node_text = node._prefix
                else:
                    assert parent['text'] == '', parent
                    prev_node['text'] = node._prefix
            else:
                prev_node['tail'] = node._prefix

        dictnode = dict(name=node_type, text=node_text, attrs=attrs, children=[], tail='')
        parent['children'].append(dictnode)

        if hasattr(node, 'children'):
            for child in reversed(node.children):
                stack.append((child, dictnode))

        # This node is previous to the next one.
        prev_node = dictnode
    prev_node['tail'] = ''  # The tail of the last element is empty

    assert len(root['children']) == 1, root['children']
    return root['children'][0]
