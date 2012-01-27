from lxml import etree

class CheetahNodeBase(etree.ElementBase):
	def find_calls(self, func_name):
		return self.xpath(
			'.//Placeholder'
			'[./CheetahVarNameChunks/CallArgString]'
			'[./CheetahVarNameChunks/DottedName="%s"]' % func_name
		)

	def remove_call(self):
		raise NotImplementedError('remove_call')

	def replace_self(self, other):
		parent = self.getparent()
		parent.replace(self, other)

	def remove_self(self):
		parent = self.getparent()
		parent.remove(self)
	
	def totext(self):
		return etree.tostring(self, method='text')

	def tostring(self, method=None):
		return etree.tostring(self, method=method)

class CheetahPlaceholder(CheetahNodeBase):
	def remove_call(self):
		args = self.xpath('./CheetahVarNameChunks/CallArgString')
		args = one(args).getchildren()

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
