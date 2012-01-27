from refactorlib.tests.util import parametrize, get_examples, get_output, assert_same_content

@parametrize(get_examples('cheetah'))
def test_can_make_round_trip(example):
	text = open(example).read()

	from refactorlib.cheetah.parse import parse
	lxmlnode = parse(text)

	from lxml.etree import tostring
	assert text == tostring(lxmlnode, method='text')

@parametrize(get_output(__file__, 'cheetah', 'xml'))
def test_matches_known_good_parsing(example, output):
	from refactorlib.cheetah.parse import parse
	example = open(example).read()
	example = parse(example).tostring()

	assert_same_content(output, example)
