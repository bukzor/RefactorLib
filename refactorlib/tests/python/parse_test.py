from refactorlib.tests.util import parametrize, get_examples, get_output

@parametrize(get_examples('python'))
def test_can_make_round_trip(example):
	example = open(example).read()

	from refactorlib.python.parse import parse
	lxmlnode = parse(example)

	from lxml.etree import tostring
	assert example == tostring(lxmlnode, method='text')

@parametrize(get_output(__file__, 'python', 'xml'))
def test_matches_known_good_parsing(example, output):
	text = open(example).read()
	xml = open(output).read()

	from refactorlib.python.parse import parse
	lxmlnode = parse(text)

	from lxml.etree import tostring
	assert xml == tostring(lxmlnode)


if __name__ == '__main__':
	test_can_make_round_trip()
