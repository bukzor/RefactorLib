from Cheetah.Parser import Parser

class InstrumentedMethod(object):
	def __init__(self, method, parent):
		self.method = method
		self.parent = parent

	def __call__(self, *args, **kwargs):
		# I want the data to be arranged in *call* order
		mydata = []
		self.parent.data.append(mydata)

		start_pos = self.parent.pos()
		result = self.method(*args, **kwargs)
		end_pos = self.parent.pos()

		mydata[:] = (start_pos, end_pos, self.method.__name__)
			
		return result


class InstrumentedParser(Parser):
	dont_care_methods = (
			'getc', 'getRowCol', 'getRowColLine', 'getLine',
			'getSilentPlaceholderToken', 'getCacheToken', 
	)
	def __init__(self, *args, **kwargs):
		super(InstrumentedParser, self).__init__(*args, **kwargs)

		self.data = []

		# Add instrumentation to certain methods
		for attr in dir(self):
			val = getattr(self, attr)
			method = self.instrument_method(val)
			if method is not None:
				setattr(self, attr, method)


	def instrument_method(self, method):
		from types import MethodType
		if not isinstance(method, MethodType):
			return
		name = method.__name__
		if name in self.dont_care_methods:
			return
		elif name.startswith('eat') or name.startswith('get'):
			return InstrumentedMethod(method, self)

	def _initDirectives(self):
		super(InstrumentedParser, self)._initDirectives()

		for key, val in self._directiveNamesAndParsers.items():
			method = self.instrument_method(val)
			if method is not None:
				self._directiveNamesAndParsers[key] = method

def parse(cheetah_content):
	from Cheetah.Compiler import Compiler
	# This is very screwy, but so is cheetah. Appologies.
	compiler = Compiler(cheetah_content)
	compiler._parser = InstrumentedParser(cheetah_content, compiler=compiler)
	compiler.compile()
	data = compiler._parser.data

	#show_data(data, cheetah_content)
	data = nice_names(data)
	data = remove_empty(data)

	dictnode = parser_data_to_dictnode(data, cheetah_content)

	from refactorlib.parse import dictnode_to_lxml
	from refactorlib.cheetah.node import CheetahNode
	return dictnode_to_lxml(dictnode, CheetahNode)

def remove_empty(data):
	for datum in data:
		start, end, method = datum
		if start != end:
			yield datum

def show_data(data, src):
	for datum in data:
		start, end, method = datum
		print method, repr(src[start:end]), start, end

def nice_names(data):
	for start, end, method in data:
		yield start, end, method_to_tag(method)

def parser_data_to_dictnode(data, src):
	root = dict(name='cheetah', start=0, end=len(src)+1, text='', tail='', attrs={}, children=[])
	stack = [root]

	for datum in dedup(data):
		start, end, name = datum
		dictnode = dict(name=name, start=start, end=end, text='', tail='', attrs={}, children=[])

		parent = stack[-1]
		while parent['end'] < end:
			if parent['end'] <= start: 
				# That's proper
				fixup_node_text(stack.pop(), src)
				parent = stack[-1]
			else:
				# That guy used backtracking! Remove him.
				# This complements, but doesn't replace, the dedup() function,
				# since backtracking functions won't necessarily fail this test
				badguy = stack.pop()
				parent = stack[-1]
				parent['children'].remove(badguy)
				#print 'removed: ', badguy

		parent['children'].append(dictnode)
		stack.append(dictnode)
	
	# clean up
	while stack:
		fixup_node_text(stack.pop(), src)

	return root

def fixup_node_text(dictnode, src):
	my = dictnode
	if my['children']:
		# my text is between my start and the first child's start
		child = my['children'][0]
		my['text'] = src[my['start']:child['start']]

		# each child's tail is between their end and the next child's start
		for next_child in my['children'][1:]:
			child['tail'] = src[child['end']:next_child['start']]
			child = next_child # The old next is the new current

		# except the last child's tail is between its end and my end
		child = my['children'][-1]
		child['tail'] = src[child['end']:my['end']]
	else:
		# If if I have no children, my text is just between my start and end
		my['text'] = src[my['start']:my['end']]

def dedup(data):
	# We want the *last* occurance of any repeated token
	# since repeats indicate backtracking.
	new_data = []
	data = tuple(data)
	for i, datum in enumerate(data):
		if datum in data[i+1:]:
			continue
		else:
			new_data.append(datum)
	return new_data

def method_to_tag(methodname):
	if methodname.startswith('eat') or methodname.startswith('get'):
		tagname = methodname[3:]
	else:
		tagname = methodname

	if tagname.endswith('Token'):
		tagname = tagname[:-5]

	return tagname
