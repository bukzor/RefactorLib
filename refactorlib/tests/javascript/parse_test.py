from refactorlib.tests.util import parametrize, get_examples, get_output, assert_same_content
from refactorlib.parse import parse

@parametrize(get_examples)
def test_can_make_round_trip(example):
	text = open(example).read()
	example = parse(example)
	# This is an artifact of smjs and its poor IO support
	assert text == example.totext()

@parametrize(get_output('xml'))
def test_matches_known_good_parsing(example, output):
	example = parse(example).tostring()
	assert_same_content(output, example)
