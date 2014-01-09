from refactorlib.tests.util import parametrize, get_examples, get_output, assert_same_content
from refactorlib.parse import parse

def simplejson_missing():
    try:
        import simplejson
        simplejson = simplejson
    except ImportError:
        return True
    else:
        return False

def check_missing():
    from refactorlib.javascript.parse import find_nodejs
    if find_nodejs() is None:
        return pytest.mark.xfail(reason='nodejs not found')
    elif simplejson_missing():
        return pytest.mark.xfail(reason='simplejson not found')
    else:
        return pytest.mark.noop

import pytest
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
