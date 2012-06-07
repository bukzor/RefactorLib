# regex taken from inducer/pudb's detect_encoding

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

	return tree

def smjs_to_dictnode(javascript_contents, tree):
	"""
	Transform a smjs structure into a dictnode, as defined by dictnode_to_lxml.
	"""
	root  = dict(name='ROOT', children=[])
	stack = [ (tree,root) ]
	prev_node = root
	#filepos = line = column = 0

	while stack:
		node, parent = stack.pop()
		node_type = node['type']

		node_text = None #TODO

		dictnode = dict(name=node_type, text=node_text, children=[], tail='')
		parent['children'].append(dictnode)
			
		children = {}
		attrs = {}
		for attr, val in node.items():
			if attr in ('loc', 'type'):
				continue
			elif isinstance(val, list):
				childlist = val
			elif isinstance(val, dict) and 'loc' in val:
				childlist = [val]
			elif isinstance(val, unicode):
				attrs[attr] = val
				continue
			else: # Should never happen
				import pudb; pudb.set_trace()

			for child in childlist:
				loc = (
						child['loc']['start']['line'],
						child['loc']['start']['column'],
						-child['loc']['end']['line'],
						-child['loc']['end']['column'],
				)
				children[loc] = child
		dictnode['attrs'] = attrs

		for loc, child in sorted(children.items(), reverse=True):
			stack.append((child, dictnode))

		# This node is previous to the next one.
		prev_node = dictnode
	prev_node['tail'] = '' # The tail of the last element is empty

	assert len( root['children'] ) == 1, root['children']
	return root['children'][0]
