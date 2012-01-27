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
		args = one(self.xpath('./CheetahVarNameChunks/CallArgString'))

		if args.text == '()':
			# no arguments.
			assert args.getchildren() == [], args.getchildren()
			self.remove_self()
			return

		args = args.getchildren()

		# remove the right paren
		assert args[-1].tail == ')', args[-1].tostring()
		args[-1].tail = ''

		if len(args) == 1 and args[0].tag == 'CheetahVar':
			#just one cheetah var
			self.replace_self(args[0])
		elif all(arg.tag == 'Py' and arg.tail == '' for arg in args):
			#just one Python identifier
			#replace the call with just the args (keep the $)
			namechunks = one(self.xpath('./CheetahVarNameChunks'))
			namechunks.clear()
			namechunks.extend(args)
		else:
			#there's something more complicated here.
			#just remove the method name (keep the $())
			one(self.xpath('./CheetahVarNameChunks/DottedName')).remove_self()
			args[-1].tail = ')' # Put it back!

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
