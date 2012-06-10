DEBUG = False

def parse(javascript_contents, encoding='ascii'):
	"""
	Given some javascript contents, as a unicode string, return the lxml representation.
	"""
	smjs_javascript = smjs_parse(javascript_contents)
	dictnode_javascript = smjs_to_dictnode(javascript_contents, smjs_javascript)
	dictnode_javascript = fixup_hierarchy(dictnode_javascript)
	dictnode_javascript = calculate_text(javascript_contents, dictnode_javascript)

	from refactorlib.parse import dictnode_to_lxml
	return dictnode_to_lxml(dictnode_javascript, encoding=encoding)

def smjs_parse(javascript_contents):
	from refactorlib import TOP
	from os.path import join
	from subprocess import Popen, PIPE
	from json import loads
	tokenizer_script = join(TOP, 'javascript/tokenize.js')

	smjs = Popen(['smjs', tokenizer_script], stdin=PIPE, stdout=PIPE)
	json = smjs.communicate(javascript_contents)[0]
	tree = loads(json)

	try:
		last_newline = javascript_contents.rindex('\n')
	except ValueError:
		last_newline = 0

	# smjs is sometimes negelectful of trailing whitespace.
	tree['loc']['end']['line'] = javascript_contents.count('\n') + 1
	tree['loc']['end']['column'] = len(javascript_contents) - last_newline

	return tree

def calculate_text(contents, tree):
	"""
	We do a pre+post order traversal of the tree to calculate the text and tail
	of each node
	"""
	pre, post = 'pre', 'post'
	index = 0
	prev_node = DictNode(name='ROOT', start=0, end=-1)
	stack = [(tree, post), (tree, pre)]
	while stack:
		node, time = stack.pop()
		if time is pre:
			nextindex = node['start']
			if prev_node is node['parent']:
				# First child.
				target = 'text'
			else:
				# Finish up previous sibling
				target = 'tail'
	
			for child in reversed(node['children']):
				stack.extend( ((child, post), (child, pre)) )
		elif time is post:
			nextindex = node['end']
			if prev_node is node:
				# Node has no children.
				target = 'text'
			else:
				# Finish up after last child.
				target = 'tail'

		prev_node[target] = contents[index:nextindex]
		if DEBUG:
			print '%-4s %s' % (time, node)
			print '     %s.%s = %r' % (prev_node, target, prev_node[target])

		# Get ready for next iteration
		index = nextindex
		prev_node = node

	# The top-level node cannot have a tail
	assert not tree.get('tail')
	tree['tail'] = None
	return tree

class DictNode(dict):
	__slots__ = ()
	def __str__(self):
		return '%s(%s-%s)' % (self['name'], self['start'], self['end'])
	@staticmethod
	def document_order(self):
		assert self['start'] <= self['end'], "Negative-width node"
		return (self['start'], -self['end'], self['index'])

def smjs_to_dictnode(javascript_contents, tree):
	"""
	Transform a smjs structure into a dictnode, as defined by dictnode_to_lxml.
	This is not a complete transformation. In particular, the nodes have no
	text or tail, and may have some overlap issues.
	"""
	from types import NoneType

	root_dictnode = DictNode(parent=None)
	stack = [(tree, root_dictnode)]
	lines = [len(line)+1 for line in javascript_contents.split('\n')]

	while stack:
		node, dictnode = stack.pop()
			
		children = []
		attrs = {}
		for attr, val in node.items():
			if attr in ('loc', 'type'):
				continue
			elif attr == 'value':
				attrs[attr] = unicode(val)
				# We would normally lose this type information, as lxml
				# wants everything to be a string.
				attrs['type'] = type(val).__name__
			elif isinstance(val, list):
				children.extend(val)
			elif isinstance(val, dict):
				if val.get('loc'):
					children.append(val)
				else:
					attrs[val['type']] = val['name']
			#elif isinstance(val, (int,unicode,type(None))):
			elif isinstance(val, unicode):
				attrs[attr] = val
			elif isinstance(val, (bool, NoneType)):
				attrs[attr] = unicode(val)
			else: # Should never happen
				import pudb; pudb.set_trace()

		dictnode.update(dict(
			name=node['type'],
			start=sum(lines[:node['loc']['start']['line']-1]) + node['loc']['start']['column'],
			end=sum(lines[:node['loc']['end']['line']-1]) + node['loc']['end']['column'],
			children=[DictNode(parent=dictnode) for child in children],
			attrs=attrs,
		))
		stack.extend(reversed(zip(children, dictnode['children'])))
	return root_dictnode

def flatten_tree(dictnode):
	index = 0
	result = []
	stack = [dictnode]
	while stack:
		dictnode = stack.pop()
		if DEBUG: print dictnode
		dictnode['index'] = index
		result.append(dictnode)
		stack.extend(reversed(dictnode.get('children', ())))
		index += 1
	return result

def fix_overlap(node, parent):
	"""We fix nodes with overlapping boundaries by widening the parent"""
	while parent is not None and node['end'] > parent['end']:
		if DEBUG: print '    Widening %s: %s -> %s' % (parent, parent['end'], node['end'])
		parent['end'] = node['end']
		parent = parent['parent']


def fixup_hierarchy(tree):
	flattened = flatten_tree(tree)

	# First fix any pre-existing issues with overlapping boundaries.
	for node in flattened:
		fix_overlap(node, node['parent'])

	# 'parents' is a stack of tree depth.  The last element is the current parent
	# node we're appending children to
	parents = []
	roots = []
	for node in sorted(flattened, key=DictNode.document_order):
		if DEBUG: print node['index'], node
		# Discard parents until the parent contains our new node
		while parents:
			parent = parents[-1]
			if node['start'] >= parent['end']:
				parents.pop()
			else:
				# We now know that parent.start <= node.start <= node.end <= parent.end
				# We've found the best parent for this node.
				if parent is not node['parent']:
					# This node needs re-parenting.
					if DEBUG: print '  Re-parenting %s: old:%s  new:%s' % (node, node['parent'], parent)
					parent['children'].append(node)
					node['parent']['children'].remove(node)
					node['parent'] = parent

				# Ensure we didn't cause new overlap errors.
				if node['end'] > parent['end']:
					raise ValueError("Overlap:\n\t%s\n\t%s" % (node, parent))

				break
		else:
			roots.append(node)

		parents.append(node)

	# Make sure all the children are in document order.
	for node in flattened:
		node['children'] = sorted(node['children'], key=DictNode.document_order)

	assert len(roots) == 1
	return roots[0]


