
def test_can_make_round_trip():
	from refactorlib.tests.util import get_examples

	for example in get_examples('cheetah'):
		text = open(example).read()

		from refactorlib.cheetah.parse import parse
		lxmlnode = parse(text)

		from lxml.etree import tostring
		assert text == tostring(lxmlnode, method='text')

def test_matches_known_good_parsing():
	from refactorlib.tests.util import get_output

	for example, xml in get_output(__file__, 'cheetah', 'xml'):
		xml = open(xml).read()
		text = open(example).read()

		from refactorlib.cheetah.parse import parse
		lxmlnode = parse(text)

		from lxml.etree import tostring
		assert xml == tostring(lxmlnode)
