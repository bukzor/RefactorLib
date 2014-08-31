from __future__ import absolute_import
from __future__ import unicode_literals

import textwrap

from refactorlib.cheetah.parse import parse


def test_not_multiline_directives():
    xmldoc = parse(textwrap.dedent("""
        #def foo(): not multiline

        #if True: not multiline

        #while False: not multiline

        #for _ in range(3): not multiline

        #inline_script: not multiline

        #call Foo: not multiline

        #filter None: not multiline
    """))

    directives = xmldoc.xpath('//Directive')
    for directive in directives:
        assert not directive.is_multiline_directive


def test_multiline_directives():
    xmldoc = parse(textwrap.dedent("""
        #def foo():
            multiline
        #end def

        #def foo()
            multiline
        #end def

        #if True
            multiline
        #end if

        #if True:
            multiline
        #end if

        #while False
            multiline
        #end while

        #while False:
            multiline
        #end while

        #for _ in range(3)
            multiline
        #end for

        #for _ in range(3):
            multiline
        #end for

        #inline_script
            multiline
        #end inline_script

        #inline_script:
            multiline
        #end inline_script

        #call foo
            multiline
        #end call

        #call foo:
            multiline
        #end call

        #filter None
            multiline
        #end filter

        #filter None:
            multiline
        #end filter
    """))

    directives = xmldoc.xpath('//Directive[not(EndDirective)]')
    for directive in directives:
        assert directive.is_multiline_directive
