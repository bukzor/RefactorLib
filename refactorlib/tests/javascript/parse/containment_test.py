
def child(start, end, children=()):
	return {
			'start': start,
			'end': end,
			'children': list(children),
			'parent': None
	}
def set_children(parent, children):
	parent['children'] = children
	for child in children:
		child['parent'] = parent
	
from refactorlib.javascript.parse import fixup_hierarchy
from py.test import raises

class TestContainment:
	def test_onechild(self):
		c1 = child(0, 1)
		c2 = child(0, 2)
		set_children(c1, [c2])
		result = fixup_hierarchy(c1)
		assert result is c1
		assert len(result['children']) == 1
		assert result['children'][0] is c2
		assert c1['end'] == c2['end'] == 2

	def test_index_preserved(self):
		c1 = child(0, 2)
		c2 = child(0, 1)
		c3 = child(0, 1)
		set_children(c1, [c3, c2])
		result = fixup_hierarchy(c1)
		assert result['children'][0] is c3
		assert result['children'][0]['children'][0] is c2

		# Reset, in opposite order.
		set_children(c1, [c2, c3])
		set_children(c3, [])
		result = fixup_hierarchy(c1)
		assert result['children'][0] is c2
		assert result['children'][0]['children'][0] is c3
		
	def test_detect_overlap(self):
		c1 = child(0, 6)
		c2 = child(2, 4)
		c3 = child(3, 5)
		set_children(c1, [c2, c3])
		with raises(ValueError):
			fixup_hierarchy(c1)
	
	def test_widening(self):
		c1 = child(0, 5)
		c2 = child(4, 5)
		c3 = child(4, 9)
		c4 = child(8, 9)
		set_children(c1, [c2, c3])
		set_children(c3, [c4])

		result = fixup_hierarchy(c1)

		# c1 gets widened to accomodate its children.
		assert c1['end'] == c4['end'] == 9
		assert result is c1
		assert result['children'][0] is c3
		assert result['children'][0]['children'][0] is c2
		assert result['children'][0]['children'][1] is c4


		
