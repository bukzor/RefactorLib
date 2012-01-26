from refactorlib.tests.util import parametrize, get_examples

@parametrize(get_examples('python'))
def test_can_make_round_trip(example):
	example = open(example).read()

	from refactorlib.python.parse import parse
	lxmlnode = parse(example)

	from lxml.etree import tostring
	assert example == tostring(lxmlnode, method='text')


if __name__ == '__main__':
	test_can_make_round_trip()
