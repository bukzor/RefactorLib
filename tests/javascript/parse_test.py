import pytest

from refactorlib.javascript.parse import find_nodejs
from refactorlib.parse import parse
from testing.util import parametrize, get_examples, get_output, assert_same_content


def simplejson_missing():
    try:
        import simplejson
        simplejson = simplejson
    except ImportError:  # pragma: no cover
        return True
    else:
        return False

if find_nodejs() is None:
    xfailif_no_js = pytest.mark.xfail(reason='nodejs not found')  # pragma: no cover
elif simplejson_missing():
    xfailif_no_js = pytest.mark.xfail(reason='simplejson not found')  # pragma: no cover
else:
    xfailif_no_js = pytest.mark.noop


@xfailif_no_js
@parametrize(get_examples)
def test_can_make_round_trip(example):
    text = open(example).read()
    example = parse(example)
    assert text == example.totext()


@xfailif_no_js
@parametrize(get_output('xml'))
def test_matches_known_good_parsing(example, output):
    example = parse(example).tostring()
    assert_same_content(output, example)


@xfailif_no_js
@parametrize(get_output('xml', func=test_matches_known_good_parsing))
def test_cli_output(example, output):
    from refactorlib.cli.xmlfrom import xmlfrom
    from refactorlib.cli.xmlstrip import xmlstrip
    xml = xmlfrom(example)
    assert_same_content(output, xml, extra_suffix='.xmlfrom')
    stripped = xmlstrip(output)
    assert_same_content(example, stripped, extra_suffix='.xmlstrip')
