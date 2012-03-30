# -*- encoding: utf8 -*-
from refactorlib.cheetah.parse import parse

def test_can_find_calls():
	"""
	The unicode "directive" isn't really a directive. 
	It gets removed from the source before parsing.
	"""
	example = parse('''
		#unicode utf8
		I like this wavy thing: ≈
	''')

	children = example.getchildren()
	assert len(children) == 1

	child = children[0]
	assert child.tag == 'PlainText'

	assert u'≈' in child.text
	assert u'#unicode' not in child.text
