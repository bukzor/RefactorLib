from testing.util import parametrize, get_examples, get_output, assert_same_content
from refactorlib.parse import parse
from . import xfailif_no_cheetah


@xfailif_no_cheetah
@parametrize(get_examples)
def test_can_make_round_trip(example):
    text = open(example).read()
    example = parse(example)
    assert text == example.totext()


@xfailif_no_cheetah
@parametrize(get_output('xml'))
def test_matches_known_good_parsing(example, output):
    example = parse(example).tostring()
    assert_same_content(output, example)


@xfailif_no_cheetah
@parametrize(get_output('xml', func=test_matches_known_good_parsing))
def test_cli_output(example, output):
    from refactorlib.cli.xmlfrom import xmlfrom
    from refactorlib.cli.xmlstrip import xmlstrip
    xml = xmlfrom(example)
    assert_same_content(output, xml, extra_suffix='.xmlfrom')
    stripped = xmlstrip(output)
    assert_same_content(example, stripped, extra_suffix='.xmlstrip')
