from refactorlib.tests.util import parametrize, get_examples, get_output, assert_same_content
from refactorlib.parse import parse

def smjs_missing():
	"""returns 0 if smjs is found on the unix $PATH"""
	from subprocess import Popen, PIPE
	p = Popen(('/usr/bin/which', 'smjs'), stdout=PIPE)
	p.communicate()
	return p.returncode

import pytest
pytestmark = pytest.mark.skipif(smjs_missing(), reason='smjs not found')


@parametrize(get_examples)
def test_can_make_round_trip(example):
	text = open(example).read()
	example = parse(example)
	assert text == example.totext()

@parametrize(get_output('xml'))
def test_matches_known_good_parsing(example, output):
	example = parse(example).tostring()
	assert_same_content(output, example)
