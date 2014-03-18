
from refactorlib.parse import parse


def test_parse_allows_you_to_explicitly_pass_source():
    ret = parse('foo.py', source='foo()\n')
    assert ret.tostring() == (
        '<file_input><simple_stmt><power><NAME>foo</NAME><trailer><LPAR>(</LPAR><RPAR>)</RPAR></trailer></power><NEWLINE>\n'
        '</NEWLINE></simple_stmt><ENDMARKER></ENDMARKER></file_input>'
    )
