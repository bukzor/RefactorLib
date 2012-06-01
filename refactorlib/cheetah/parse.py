from Cheetah.Parser import Parser

DEBUG = False

class InstrumentedEnclosureList(list):
	def __init__(self, iterable=None, **kwargs):
		self.parent = kwargs.pop('parent')
		self.__data = {}
		if iterable is None:
			iterable = ()
		for enclosure in iterable:
			self.notify_parent(enclosure)
		super(InstrumentedEnclosureList, self).__init__(iterable, **kwargs)
	
	def append(self, enclosure):
		self.notify_parent(enclosure)
		return super(InstrumentedEnclosureList, self).append(enclosure)
	
	def notify_parent(self, enclosure):
		name, start_pos = enclosure
		mydata = [start_pos, None, name]
		self.__data[enclosure] = mydata

		# Check for backtracking
		index = -1
		datalen = len(self.parent.data)
		while datalen > -index and self.parent.data[index][0] > start_pos:
			index -= 1
		index += 1

		if index == 0:
			self.parent.data.append(mydata)
		else:
			self.parent.data.insert(index, mydata)

	def pop(self):
		enclosure = super(InstrumentedEnclosureList, self).pop()
		mydata = self.__data[enclosure]
		# Unfortunately, cheetah pops the enclosure *before* advancing its position
		mydata[1] = self.parent.pos() + 1
		return enclosure


class InstrumentedMethod(object):
	def __init__(self, method, parent, **args):
		self.method = method
		self.parent = parent
		self.args = args

	def __call__(self, *args, **kwargs):
		# I want the data to be arranged in *call* order
		start_pos = self.parent.pos()
		name = self.method.__name__

		for arg, cls in self.args.items():
			kwargs[arg] = cls(kwargs.get(arg), parent=self.parent)

		mydata = [start_pos, None, name]
		self.parent.data.append(mydata)
		result = self.method(*args, **kwargs) # Call the wrapped method.
		mydata[1] = self.parent.pos()
			
		return result

class AnyString(unicode):
	'Represents "any string".'
	def startswith(self, other):
		return True
	def __eq__(self, other):
		return True

from collections import defaultdict
class AutoDict(defaultdict):
	"Like defaultdict, but auto-populates for .get() as well."
	no_default = []
	def get(self, key, default=no_default):
		if default is self.no_default:
			return self[key]
		else:
			return super(AutoDict, self).get(key, default)

class InstrumentedParser(Parser):
	dont_care_methods = (
			'getc', 'getRowCol', 'getRowColLine', 'getLine',
			'getSilentPlaceholderToken', 'getCacheToken', 
	)
	def __init__(self, *args, **kwargs):
		super(InstrumentedParser, self).__init__(*args, **kwargs)

		self.data = []
		self._openDirectivesDataStack = []

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
		elif name == 'getExpressionParts':
			# 'getExpression' also has an enclosure argument, but it doesn't seem to be important
			return InstrumentedMethod(method, self, enclosures=InstrumentedEnclosureList)
		elif name.startswith('eat') or name.startswith('get'):
			return InstrumentedMethod(method, self)

	def _initDirectives(self):
		super(InstrumentedParser, self)._initDirectives()

		# Cheetah supports #unicode directives, but doesn't implement it in the
		# parser, so I have to...
		self._directiveNamesAndParsers['unicode'] = None
		self._simpleExprDirectives.append('unicode')
		self._compiler.addUnicode = lambda expr: None

		for key, val in self._directiveNamesAndParsers.items():
			method = self.instrument_method(val)
			if method is not None:
				self._directiveNamesAndParsers[key] = method

		# We need unrecognized directives to be seen as macros
		self._directiveNamesAndParsers[AnyString()] = self.eatMacroCall
		self._directiveNamesAndParsers = AutoDict(lambda: self.eatMacroCall, self._directiveNamesAndParsers)
		fake_macro = lambda **kwargs: ''
		self._macros = AutoDict(lambda: fake_macro, self._macros)

	def pushToOpenDirectivesStack(self, directiveName):
		result = super(InstrumentedParser, self).pushToOpenDirectivesStack(directiveName)

		# This properly goes just before the previous eatDirective
		for i, (start, end, name) in enumerate(reversed(self.data), 1):
			if name == 'eatDirective':
				break

		index = len(self.data) - i
		self._openDirectivesDataStack.append((index, start))

		return result

	def popFromOpenDirectivesStack(self, directiveName):
		result = super(InstrumentedParser, self).popFromOpenDirectivesStack(directiveName)

		directive_index, mystart = self._openDirectivesDataStack.pop()
		myend = self.pos()

		# Have to check for children that started before eatDirective (e.g. decorators)
		myindex = directive_index
		for i, (start, end, name) in enumerate(reversed(self.data[:directive_index]), 1):
			if start <= mystart and mystart < end < myend:
				mystart = min(start, mystart)
				myindex = directive_index - i

		data = [mystart, myend, directiveName]
		self.data.insert(myindex, data)
		

		return result

def detect_encoding(source):
	from Cheetah.Parser import unicodeDirectiveRE, encodingDirectiveRE
	unicodeMatch = unicodeDirectiveRE.search(source)
	if unicodeMatch:
		return unicodeMatch.group(1)
	encodingMatch = encodingDirectiveRE.search(source)
	if encodingMatch:
		return encodingMatch.group(1)
	
	# We didn't find anything.
	return None

def parse(cheetah_content, encoding=None):

	from Cheetah.Compiler import Compiler
	# This is very screwy, but so is cheetah. Apologies.
	compiler = Compiler()
	compiler._parser = InstrumentedParser(cheetah_content, compiler=compiler)
	compiler.compile()
	data = compiler._parser.data

	if DEBUG:
		data = show_data(data, cheetah_content)
	data = nice_names(data)
	data = remove_empty(data)
	data = dedup(data)

	dictnode = parser_data_to_dictnode(data, cheetah_content)

	from refactorlib.parse import dictnode_to_lxml
	from refactorlib.cheetah.node import node_lookup
	root = dictnode_to_lxml(dictnode, node_lookup, encoding)
	return root

def remove_empty(data):
	for datum in data:
		start, end, method = datum
		if start != end:
			yield datum

def show_data(data, src):
	for datum in data:
		start, end, method = datum
		print method, repr(src[start:end]), start, end
		yield datum

def nice_names(data):
	for start, end, method in data:
		yield start, end, method_to_tag(method)

def parser_data_to_dictnode(data, src):
	root = dict(name='cheetah', start=0, end=len(src)+1, text='', tail='', attrs={}, children=[])
	stack = [root]

	for datum in data:
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
				if DEBUG:
					print 'Removed bad:', badguy

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
	"""
	Cheetah does a lot of backtracking.
	We can fix it!
	"""
	new_data = [] # Can't yield. We need to look behind.
	file_pointer = 0
	for datum in data:
		start, end, name = datum

		if start > file_pointer: 
			# New data.
			file_pointer = start
			new_data.append(datum)
			continue

		dup_index = None
		for i, d in enumerate(reversed(new_data)):
			if d == datum:
				dup_index = -1 - i
				break
			elif d[0] < start:
				break

		if dup_index is None:
			new_data.append(datum)
		elif file_pointer == start:
			# Dupe: This is a simple backtrack, take the latest parsing.
			if DEBUG:
				print "Duped:", datum
			del new_data[dup_index]
			new_data.append(datum)
		else:
			# Dupe: We've advanced beyond this data, drop it.
			if DEBUG:
				print "Dropped:", datum
			pass
	return new_data

def method_to_tag(methodname):
	if methodname == '[':
		return 'SquareBracket'
	elif methodname == '{':
		return 'CurlyBrace'
	elif methodname == '(':
		return 'Paren'

	if methodname.startswith('eat') or methodname.startswith('get'):
		tagname = methodname[3:]
	else:
		tagname = methodname

	if tagname.endswith('Token'):
		tagname = tagname[:-5]

	return tagname
