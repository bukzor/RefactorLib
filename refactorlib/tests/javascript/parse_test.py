from refactorlib.tests.util import parametrize, get_examples, get_output, assert_same_content
from refactorlib.parse import parse

def nodejs_missing():
    """returns 0 if nodejs is found on the unix $PATH"""
    from subprocess import Popen, PIPE
    p = Popen(('/usr/bin/which', 'node'), stdout=PIPE)
    p.communicate()
    return p.returncode

def simplejson_missing():
    try:
        import simplejson
        simplejson = simplejson
    except ImportError:
        return True
    else:
        return False

def check_missing():
    if nodejs_missing():
        return pytest.mark.skipif(True, reason='nodejs not found')
    elif simplejson_missing():
        return pytest.mark.skipif(True, reason='simplejson not found')
    else:
        return pytest.mark.skipif(False, reason='nothing missing')

import pytest
# I'd like to use multiple skipif marks here, but the messages get mixed up.
pytestmark = check_missing()

@parametrize(get_examples)
def test_can_make_round_trip(example):
    text = open(example).read()
    example = parse(example)
    assert text == example.totext()

@parametrize(get_output('xml'))
def test_matches_known_good_parsing(example, output):
    example = parse(example).tostring()
    assert_same_content(output, example)

@parametrize(get_output('xml', func=test_matches_known_good_parsing))
def test_cli_output(example, output):
    from refactorlib.cli.xmlfrom import xmlfrom
    from refactorlib.cli.xmlstrip import xmlstrip
    xml = xmlfrom(example)
    assert_same_content(output, xml, extra_suffix='.xmlfrom')
    stripped = xmlstrip(output)
    assert_same_content(example, stripped, extra_suffix='.xmlstrip')
