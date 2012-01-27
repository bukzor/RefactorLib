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
	
	def totext(self):
		return etree.tostring(self, method='text')

	def tostring(self, method=None):
		return etree.tostring(self, method=method)


__all__ = ('RefactorLibNodeBase',)
