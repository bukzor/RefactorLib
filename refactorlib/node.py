"""
Some basic additions to the lxml element node class.
"""
from lxml import etree

class RefactorLibNodeBase(etree.ElementBase):
	def remove_call(self):
		raise NotImplementedError('remove_call')

	def replace_self(self, other):
		parent = self.getparent()
		parent.replace(self, other)

	def remove_self(self):
		parent = self.getparent()
		parent.remove(self)
	
	def totext(self, with_tail=True):
		return etree.tostring(self, method='text', with_tail=with_tail)

	def tostring(self, method=None, with_tail=True):
		return etree.tostring(self, method=method, with_tail=with_tail)
	
	def following_text(self):
		"""
		Get the first non-empty piece of text after this node.
		See also: http://lxml.de/tutorial.html#using-xpath-to-find-text
		"""
		return one(self.xpath('./following::text()[.!=""][1]'))

	def preceding_text(self):
		"""
		Get the first non-empty piece of text before this node.
		See also: http://lxml.de/tutorial.html#using-xpath-to-find-text
		"""
		return one(self.xpath('./preceding::text()[.!=""][1]'))

	def clear_indent(self):
		"""
		Clear any indent preceding this node.
		"""
		indent = self.preceding_text()
		attr = 'text' if indent.is_text else 'tail'
		indent_owner = indent.getparent()
		setattr(indent_owner, attr, indent.rstrip(' \t'))
	
	def xpath_one(self, xpath):
		return one(self.xpath(xpath))

def one(mylist):
	"""
	assert that there's only one thing, and get it.
	"""
	if len(mylist) != 1:
		raise ValueError(
				'Expected exactly one item. Got %i: %r'
				% (
					len(mylist),
					list(
						item.tostring() 
						if isinstance(item, etree.ElementBase)
						else item
						for item in mylist
					)
				)
		)

	return mylist[0]

__all__ = ('RefactorLibNodeBase',)
