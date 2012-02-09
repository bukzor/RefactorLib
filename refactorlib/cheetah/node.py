"""
cheetah-specific additions to the lxml element node class.
"""
from lxml import etree
from refactorlib.node import RefactorLibNodeBase, one

class CheetahNodeBase(RefactorLibNodeBase):
	def find_calls(self, func_name):
		return self.xpath(
			'.//Placeholder'
			'[./CheetahVarNameChunks/CallArgString]'
			'[./CheetahVarNameChunks/DottedName="%s"]' % func_name
		) + self.xpath(
			'.//CheetahVar'
			'[./CheetahVarBody/CheetahVarNameChunks/CallArgString]'
			'[./CheetahVarBody/CheetahVarNameChunks/DottedName="%s"]' % func_name
		)

	def find_decorators(self, dec_name):
		return self.xpath( './/Decorator[./Expression="%s"]' % dec_name )

	def get_enclosing_blocks(self):
		"""
		Get the nodes representing the blocks that enclose this node.
		"""
		# TODO: unit test, with decorators
		return self.xpath(
				# Grab directives that are our direct ancestor.
				'./ancestor::Directive'
				'|' # OR:
				# Look at all ancestors.
				'./ancestor::*'
				# Its last child element should be an EndDirective.
				'[./*[last()][self::Directive]/*[1][self::EndDirective]]'
				# Grab the first child. Require that it's a directive
				'/*[1][self::Directive]'
				# Use the first directive that's not a Decorator.
				'/descendant-or-self::Directive[not(./Decorator)]'
		)
	
	def add_comment(self, comment):
		# TODO: unit test
		text = self.preceding_text()
		while '\n' not in text:
			text = text.getparent().preceding_text()
		parent = text.getparent()
		attr = 'text' if text.is_text else 'tail'
		text = text.replace(
				'\n',
				'\n%s\n' % comment,
				1
		)
		setattr(parent, attr, text)

	def is_in_context(self, directive_string):
		try:
			directive_name, var = directive_string.split(None, 1)
		except ValueError:
			directive_name, var = directive_string.strip(), None

		directive_name = directive_name.lstrip('#')
		root = self.getroottree().getroot()

		for directive in self.get_enclosing_blocks():
			if (
					# TODO: create a Directive and simply compare
					directive.name == directive_name and
					(
						directive.var is None and var is None or
						directive.var.totext(with_tail=False) == var
					)
			):
				return True

			if directive.name == 'def':
				func = directive.var.totext(with_tail=False)
				for call in root.find_calls(func):
					if call.is_in_context(directive_string):
						return True
		else:
			return False

class _CheetahVariable(CheetahNodeBase):
	"""
	This class represents a cheetah placeholder, such as: $FOO
	"""
	def _remove_call(self, args_body):
		args_token = one(args_body.xpath('./CheetahVarNameChunks/CallArgString'))
		args = args_token.getchildren()

		if not args: # no arguments.
			assert args_token.totext().strip('(\n\t )') == '', args_token.totext()
			self.remove_self()
			return


		if len(args) == 1 and (
				args[0].tag == 'CheetahVar'
				or (
					args[0].tag == 'Py'
					and len(args[0].text) >= 2
					and args[0].text[0] == args[0].text[-1]
					and args[0].text[0] in '"'"'"
				)
		):
			#just one cheetah var / Python string
			arg = args[0]
			self.replace_self(arg)
			# replace the right paren with whatever followed the `self` token
			assert arg.tail.strip() == ')', repr(arg.tostring())
			arg.tail = self.tail
		elif (
				# Python tokens without spaces
				all(arg.tag == 'Py' for arg in args) and
				all(arg.tail == '' for arg in args[:-1]) and
				args[-1].tail.strip() == ')'
		):
			#just one Python variable.
			#replace the call with just the args (keep the $)
			namechunks = one(args_body.xpath('./CheetahVarNameChunks'))
			namechunks.clear()
			namechunks.extend(args)
			assert args[-1].tail.strip() == ')', repr(arg.tostring())
			args[-1].tail = ''
		else:
			#there's something more complicated here.
			#just remove the method name (keep the $())
			one(args_body.xpath('./CheetahVarNameChunks/DottedName')).remove_self()

class CheetahPlaceholder(_CheetahVariable):
	def remove_call(self):
		args_body = self
		super(CheetahPlaceholder, self)._remove_call(args_body)

class CheetahVar(_CheetahVariable):
	def remove_call(self):
		args_body = one(self.xpath('./CheetahVarBody'))
		super(CheetahVar, self)._remove_call(args_body)


class CheetahDecorator(CheetahNodeBase):
	def remove_self(self):
		children = self.getchildren()
		assert children[0].tag == 'DirectiveStart', children[0]
		assert children[1].tag == 'Expression', children[1]

		parent = self.getparent()
		index = parent.index(self)

		self.clear_indent()
		parent.remove(self)

		# put some contents back, if necessary
		for child in children[-1:1:-1]:
			parent.insert(index, child)

class CheetahDirective(CheetahNodeBase):
	def replace_directive(self, other):
		if isinstance(other, basestring):
			var = CheetahNode('CheetahVar')
			try:
				directive, var.text = other.split(None, 1)
			except ValueError:
				directive, var.text = other.strip(), ''
			directive = directive.lstrip('#')
		else:
			raise NotImplementedError("Patches Are Welcome!")
			directive = other.name
			var = other.xpath('.//CheetahVar')[0]
		
		self.name = directive
		self.var = var
		
		if self.is_multiline_directive:
			# Multi-line form: Need to update the end directive.
			end_expression = self.get_end_directive().xpath_one('./EndDirective/Expression')
			tail = end_expression.tail
			end_expression.clear()
			end_expression.text = directive
			end_expression.tail = tail
	
	@property
	def is_multiline_directive(self):
		return not self.xpath('./EndDirective or ./SimpleExprDirective or .//text()=":"')
	
	def __get_name(self):
		"The name of the directive. The word just after the first # sign."
		return self.xpath_one('./*/*[1][self::DirectiveStart]').tail

	def __set_name(self, val):
		self.xpath_one('./*/*[1][self::DirectiveStart]').tail = val

	name = property(__get_name, __set_name)

	def __get_var(self):
		try:
			return self.xpath_one('./*/CheetahVar | ./*/Identifier')
		except ValueError:
			return None

	def __set_var(self, var):
		old_var = self.var
		
		if old_var is None:
			self.append(var)
		else:
			var.tail = old_var.tail
			old_var.replace_self(var)

	var = property(__get_var, __set_var)

	def get_end_directive(self):
		"""
		Returns the EndDirective node that logically matches this Directive.
		"""
		# Look at sibling Directives after this node, take first one that is an EndDirective.
		return self.xpath_one('./following-sibling::Directive[./EndDirective][1]')

class CheetahNodeLookup(etree.PythonElementClassLookup):
	"""
	Specify how to assign Python classes to lxml objects.
	see: http://lxml.de/element_classes.html#tree-based-element-class-lookup-in-python
	"""
	def lookup(self, document, element):
		if element.tag == 'Placeholder':
			return CheetahPlaceholder
		elif element.tag == 'CheetahVar':
			return CheetahVar
		elif element.tag == 'Directive':
			return CheetahDirective
		elif element.tag == 'Decorator':
			return CheetahDecorator
		else:
			return CheetahNodeBase

CHEETAH_PARSER = etree.XMLParser()
CHEETAH_PARSER.set_element_class_lookup(CheetahNodeLookup())

CheetahNode = CHEETAH_PARSER.makeelement

__all__ = ('CheetahNode',)
