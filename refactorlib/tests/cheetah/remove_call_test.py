from refactorlib.tests.util import parametrize, get_output, assert_same_content
from . import pytestmark

def test_can_find_calls():
    from refactorlib.cheetah.parse import parse

    example = parse('''
        foo $foo() bar
    ''')

    calls = example.find_calls('foo')
    assert len(calls) == 1
    assert calls[0].totext() == '$foo()'

@parametrize(get_output)
def test_can_remove_calls(example, output):
    from refactorlib.cheetah.parse import parse
    example = open(example).read()
    example = parse(example)

    calls = example.find_calls('foo')
    assert len(calls) == 5

    for call in calls:
        call.remove_call()

    # Check the text.
    example = example.totext()
    assert_same_content(output, example)

