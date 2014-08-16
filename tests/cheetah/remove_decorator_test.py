from testing.util import parametrize, get_output, assert_same_content
from . import xfailif_no_cheetah


@xfailif_no_cheetah
@parametrize(get_output)
def test_remove_foo(example, output):
    from refactorlib.cheetah.parse import parse
    example = open(example).read()
    example = parse(example)

    for decorator in example.find_decorators('@foo'):
        decorator.remove_self()

    # Check the text.
    example = example.totext()
    assert_same_content(output, example)


@xfailif_no_cheetah
@parametrize(get_output)
def test_remove_foo_dot_bar(example, output):
    from refactorlib.cheetah.parse import parse
    example = open(example).read()
    example = example.replace('#@foo\n', '#@foo.bar\n')
    example = parse(example)

    for decorator in example.find_decorators('@foo.bar'):
        decorator.remove_self()

    # Check the text.
    example = example.totext()
    assert_same_content(output, example)
