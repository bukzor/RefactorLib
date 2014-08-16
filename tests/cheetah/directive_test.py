from testing.util import parametrize, get_output, assert_same_content
from . import xfailif_no_cheetah


@xfailif_no_cheetah
@parametrize(get_output('txt'))
def test_find_end_directive(example, output):
    text = open(example).read()

    from refactorlib.cheetah.parse import parse
    lxmlnode = parse(text)
    tree = lxmlnode.getroottree()

    new_output = []
    for directive in lxmlnode.xpath('//Directive'):
        new_output.append(
            'Directive: %s' % tree.getpath(directive),
        )
        if directive.is_multiline_directive:
            new_output.append(
                'End: %s' % tree.getpath(directive.get_end_directive()),
            )
        else:
            new_output.append(
                'Single-line: %s' % directive.totext()
            )
        new_output.append('')

    new_output = '\n'.join(new_output)
    assert_same_content(output, new_output)


@xfailif_no_cheetah
@parametrize(get_output)
def test_replace_directive(example, output):
    from refactorlib.parse import parse
    lxmlnode = parse(example)

    for directive in lxmlnode.xpath('//Directive'):
        if directive.xpath('./EndDirective'):
            # Don't mess with #end statements
            continue

        if directive.var is None:
            directive.replace_directive('#{{{%s}}}' % directive.name)
        else:
            directive.replace_directive('#{{{%s}}} [%s]' % (directive.name, directive.var.totext(with_tail=False)))

    new_output = lxmlnode.totext()
    assert_same_content(output, new_output)


@xfailif_no_cheetah
@parametrize(get_output('txt'))
def test_get_enclosing_blocks(example, output):
    text = open(example).read()

    from refactorlib.cheetah.parse import parse
    lxmlnode = parse(text)
    tree = lxmlnode.getroottree()

    unique_contexts = {}
    for directive in lxmlnode.xpath('//Directive'):
        context = tuple(
            tree.getpath(block) for block in directive.get_enclosing_blocks()
        )

        if context and context not in unique_contexts:
            unique_contexts[context] = directive

    new_output = []
    for context, directive in sorted(unique_contexts.items()):
        new_output.append(
            'Directive: %s' % tree.getpath(directive)
        )
        for c in context:
            new_output.append('  ' + c)
        new_output.append('')

    new_output = '\n'.join(new_output)
    assert_same_content(output, new_output)
