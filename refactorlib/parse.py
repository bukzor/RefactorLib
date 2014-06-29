# -*- coding: UTF-8 -*-


def parse(filename, filetype=None, encoding=None):
    from refactorlib.filetypes import FILETYPES
    filetype = FILETYPES.detect_filetype(filename, filetype)

    source = open(filename).read()

    # If no encoding was explicitly specified, see if we can parse
    # it out from the contents of the file.
    if encoding is None:
        encoding = filetype.encoding_detector(source)

    if encoding:
        source = unicode(source, encoding)
    else:
        # I don't see why encoding=None is different from not specifying the encoding.
        source = unicode(source)

    return filetype.parser(source, encoding)


def dictnode_to_lxml(tree, node_lookup=None, encoding=None):
    """
    Input: A dictionary-based representation of a node tree.
    Output: An lxml representation of the same.

    Each dictionary has three attributes:
        name -- The type of node, a string. In html, this would be the tag name.
        text -- The content of the node: <b>text</b>
        tail -- Any content after the end of this node, but before the start of the next: <br/>tail
        attrs -- A dictionary of any extra attributes.
        children -- An ordered list of more node-dictionaries.
    """
    if not node_lookup:
        from refactorlib.node import node_lookup

    from lxml.etree import XMLParser, fromstring
    lxml_parser_object = XMLParser(encoding=encoding)
    lxml_parser_object.set_element_class_lookup(node_lookup)
    Element = lxml_parser_object.makeelement

    root = None
    stack = [(tree, root)]

    while stack:
        node, parent = stack.pop()

        if parent is None:
            # We use this roundabout method becuase the encoding is always set
            # to 'UTF8' if we use parser.makeelement()
            lxmlnode = fromstring('<trash></trash>', parser=lxml_parser_object)
            lxmlnode.tag = node['name']
            lxmlnode.attrib.update(node.get('attrs', {}))
            root = lxmlnode
        else:
            lxmlnode = Element(node['name'], attrib=node.get('attrs', {}))
            parent.append(lxmlnode)

        lxmlnode.text = node['text']
        lxmlnode.tail = node['tail']

        for child in reversed(node['children']):
            stack.append((child, lxmlnode))

    return root
