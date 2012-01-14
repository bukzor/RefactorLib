
def dictnode_to_lxml(tree):
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
	from lxml.etree import Element

	root = Element('ROOT')
	stack = [ (tree,root) ]

	while stack:
		node, parent = stack.pop()

		lxmlnode = Element(node['name'], attrib=node['attrs'])
		lxmlnode.text = node['text']
		lxmlnode.tail = node['tail']
		parent.append(lxmlnode)

		for child in reversed(node['children']):
			stack.append((child, lxmlnode))

	children = root.getchildren()
	assert len( children ) == 1, children
	return children[0]
