from testing.util import parametrize, get_output, assert_same_content
from . import xfailif_no_cheetah


@xfailif_no_cheetah
@parametrize(get_output('txt'))
def test_is_in_context(example, output):
    from refactorlib.parse import parse

    lxmlnode = parse(example)

    top_level_directives = lxmlnode.xpath('/cheetah/*/*[1][self::Directive]')
    top_level_directives = [
        b'#' + d.name.encode('UTF-8') + b' ' + d.var.totext(with_tail=False)
        if d.var is not None else
        b'#' + d.name.encode('UTF-8')
        for d in top_level_directives
    ]

    # for each Placeholder, print if it's "in context" of each top-level
    # directive

    new_output = []
    for placeholder in lxmlnode.xpath('//Placeholder'):
        new_output.append(
            b'Placeholder: ' + placeholder.totext(with_tail=False)
        )
        for d in top_level_directives:
            new_output.append(
                b'    ' + d + b' ' +
                str(placeholder.is_in_context(d)).encode('UTF-8')
            )
        new_output.append(b'')

    new_output = b'\n'.join(new_output)
    assert_same_content(output, new_output)
