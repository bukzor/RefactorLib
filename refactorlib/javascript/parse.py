DEBUG = False

def parse(javascript_contents, encoding='ascii'):
	"""
	Given some javascript contents, as a unicode string, return the lxml representation.
	"""
	smjs_javascript = smjs_parse(javascript_contents)
	dictnode_javascript = smjs_to_dictnode(javascript_contents, smjs_javascript)

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
	except ValueError: # no newlines in that file
		pass
	else:
		tree['loc']['end']['line'] = javascript_contents.count('\n') + 1
		tree['loc']['end']['column'] = len(javascript_contents) - last_newline

	return tree


def smjs_to_dictnode(javascript_contents, tree):
	"""
	Transform a smjs structure into a dictnode, as defined by dictnode_to_lxml.
	"""
	root  = dict(name='ROOT', children=[])
	stack = [ (tree,root,'post'), (tree,root,'pre') ]
	prev_dictnode = root
	lines = javascript_contents.split('\n')
	line = column = 0

	def update_prev_node():
		if when == 'pre':
			nextline = node['loc']['start']['line']
			nextcol = node['loc']['start']['column']
			if prev_dictnode is parent:
				# First child.
				target = 'text'
			else:
				# Finish up previous sibling
				target = 'tail'
		elif when == 'post':
			nextline = node['loc']['end']['line']
			nextcol = node['loc']['end']['column']
			if prev_dictnode is node.get('dictnode'):
				# Node has no children.
				if DEBUG: print 'no child', when
				target = 'text'
			else:
				# Finish up after last child.
				target = 'tail'


		# Lines from the smjs parser are one-based
		nextline -= 1
		if DEBUG:
			print '(%s, %s) (%s, %s)' % (
					node['loc']['start']['line'],
					node['loc']['end']['line'],
					node['loc']['start']['column'],
					node['loc']['end']['column'],
			), when, node['type']
			print parent['name'], 
			print '%s.%s =' % (prev_dictnode['name'], target),
			

		if nextline == line:
			contents = lines[line][column:nextcol]
		else:
			contents = '\n'.join(
				# Leftovers from earlier.
				[lines[line][column:]] +
				# In-between lines.
				lines[line+1:nextline] +
				# Get any content from nextline
				[lines[nextline][:nextcol]]
			)
		if DEBUG: print repr(contents)
		prev_dictnode[target] = contents
		return nextline, nextcol

	while stack:
		node, parent, when = stack.pop()
		line, column = update_prev_node()
		if when == 'post':
			prev_dictnode = node['dictnode']
			continue

		dictnode = dict(name=node['type'], children=[], text=None, tail=None)
		node['dictnode'] = dictnode
		parent['children'].append(dictnode)
			
		children = []
		attrs = {}
		for attr, val in node.items():
			if attr in ('loc', 'type', 'dictnode'):
				continue
			elif isinstance(val, list):
				children.extend(val)
			elif isinstance(val, dict):
				if val.get('loc'):
					children.append(val)
				else:
					attrs[val['type']] = val['name']
			elif isinstance(val, (int,unicode,type(None))):
				attrs[attr] = unicode(val)
				continue
			else: # Should never happen
				import pudb; pudb.set_trace()
		dictnode['attrs'] = attrs

		children = resolve_containment(children)
		for child in reversed(children):
			stack.extend( ((child, dictnode, 'post'), (child, dictnode, 'pre')) )

		# This node is previous to the next one.
		prev_dictnode = dictnode

	assert len( root['children'] ) == 1, root['children']
	return root['children'][0]


def resolve_containment(children):
	from collections import namedtuple
	Node = namedtuple('Node', 'start end index child')
	tmp = []
	for index, child in enumerate(children):
		child['children'] = []
		tmp.append(Node(
				(child['loc']['start']['line'], child['loc']['start']['column']),
				(child['loc']['end']['line'], child['loc']['end']['column']),
				index,
				child,
		))
	def document_order(node):
		return (node.start[0], node.start[1], -node.end[0], -node.end[1], node.index)

	# 'parents' is a stack of tree depth.  The last element is the current parent
	# node we're appending children to
	parents = []
	roots = []
	for node in sorted(tmp, key=document_order):
		assert node.start <= node.end

		# Discard parents until the parent contains our new node
		while parents:
			parent = parents[-1]
			if node.start >= parent.end:
				parents.pop()
			# We now know that parent.start <= node.start < parent.end
			elif node.end > parent.end:
				raise ValueError("Overlap:\n\t%r\n\t%r" % (node, parent))
			# We now know that parent.start <= node.start <= node.end <= parent.end
			# Add the node as a child of that parent.
			else:
				parent.child['children'].append(node.child)
				break
		else:
			roots.append(node.child)

		parents.append(node)
	return roots


