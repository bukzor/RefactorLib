def parse(filename, filetype=None, encoding=None):
    from refactorlib.filetypes import FILETYPES
    filetype = FILETYPES.detect_filetype(filename, filetype)

    source = open(filename, 'rb').read()

    # If no encoding was explicitly specified, see if we can parse
    # it out from the contents of the file.
    if encoding is None:
        encoding = filetype.encoding_detector(source)

    encoding = encoding if encoding else 'UTF-8'
    source = source.decode(encoding)

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

    from lxml.etree import Element, XMLParser

    root = None
    stack = [(tree, root)]

    while stack:
        node, parent = stack.pop()

        # sort attributes for determinism
        attrs = node.get('attrs', {})
        attrs = {k: attrs[k] for k in sorted(attrs)}

        if parent is None:
            # We use this roundabout method becuase the encoding is always set
            # to 'UTF8' if we use parser.makeelement()
            parser = XMLParser(encoding=encoding)
            parser.set_element_class_lookup(node_lookup)
            parser.feed(b'<a/>')
            lxmlnode = parser.close()
            lxmlnode.tag = node['name']
            lxmlnode.attrib.update(attrs)
            root = lxmlnode
        else:
            lxmlnode = Element(node['name'], attrib=attrs)
            parent.append(lxmlnode)

        lxmlnode.text = node['text']
        lxmlnode.tail = node['tail']

        for child in reversed(node['children']):
            stack.append((child, lxmlnode))

    return root
