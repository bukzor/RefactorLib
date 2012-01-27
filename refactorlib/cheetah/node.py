"""
cheetah-specific additions to the lxml element node class.
"""
from lxml import etree
from refactorlib.node import RefactorLibNodeBase

class CheetahNodeBase(RefactorLibNodeBase):
	def find_calls(self, func_name):
		return self.xpath(
			'.//Placeholder'
			'[./CheetahVarNameChunks/CallArgString]'
			'[./CheetahVarNameChunks/DottedName="%s"]' % func_name
		)

class CheetahPlaceholder(CheetahNodeBase):
	"""
	This class represents a cheetah placeholder, such as: $FOO
	"""
	def remove_call(self):
		args_token = one(self.xpath('./CheetahVarNameChunks/CallArgString'))
		args = args_token.getchildren()

		
		if not args: # no arguments.
			assert args_token.text.strip('(\n\t )') == '', args_token.totext()
			self.remove_self()
			return


		if len(args) == 1 and args[0].tag == 'CheetahVar':
			#just one cheetah var
			arg = args[0]
			self.replace_self(arg)
			# remove the right paren
			assert arg.tail.strip() == ')', repr(arg.tostring())
			arg.tail = ''
		elif (
				# Python tokens without spaces
				all(arg.tag == 'Py' for arg in args) and
				all(arg.tail == '' for arg in args[:-1]) and
				args[-1].tail.strip() == ')'
		):
			#just one Python identifier
			#replace the call with just the args (keep the $)
			namechunks = one(self.xpath('./CheetahVarNameChunks'))
			namechunks.clear()
			namechunks.extend(args)
			args[-1].tail = ''
		else:
			#there's something more complicated here.
			#just remove the method name (keep the $())
			one(self.xpath('./CheetahVarNameChunks/DottedName')).remove_self()

def one(mylist):
	"""
	assert that there's only one thing, and get it.
	"""
	assert len(mylist) == 1, tuple(item.tostring() for item in mylist)
	return mylist[0]

class CheetahNodeLookup(etree.PythonElementClassLookup):
	"""
	Specify how to assign Python classes to lxml objects.
	see: http://lxml.de/element_classes.html#tree-based-element-class-lookup-in-python
	"""
	def lookup(self, document, element):
		if element.tag == 'Placeholder':
			return CheetahPlaceholder
		else:
			return CheetahNodeBase

CHEETAH_PARSER = etree.XMLParser()
CHEETAH_PARSER.set_element_class_lookup(CheetahNodeLookup())

CheetahNode = CHEETAH_PARSER.makeelement

__all__ = ('CheetahNode',)
