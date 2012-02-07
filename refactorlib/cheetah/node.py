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
		return self.xpath(
				'.//Decorator'
				'[./Expression/ExpressionParts/Py[2]="%s"]' % dec_name
		)

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
			directive = other.xpath('.//DirectiveStart')[0].tail.strip()
			var = other.xpath('.//CheetahVar')[0]
		
		self.xpath_one('.//DirectiveStart[1]').tail = directive
		self.xpath_one('.//CheetahVar[1]').replace_self(var)
		
		if self.is_multiline_directive:
			# Multi-line form: Need to update the end directive.
			end_expression = self.find_end_directive().xpath_one('./Expression[1]')
			end_expression.clear()
			end_expression.text = directive
	
	@property
	def is_multiline_directive(self):
		return not self.xpath('./EndDirective or ./SimpleExprDirective or .//text()=":"')

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
