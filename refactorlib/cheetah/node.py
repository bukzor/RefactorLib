"""
cheetah-specific additions to the lxml element node class.
"""
from lxml import etree
from refactorlib.node import RefactorLibNodeBase, one


class CheetahNodeBase(RefactorLibNodeBase):
    def find_calls(self, func_name):
        if isinstance(func_name, bytes):
            func_name = func_name.decode('UTF-8')
        return self.xpath(
            f'.//Placeholder[./Identifier="{func_name}"]',
        ) + self.xpath(
            f'.//CheetahVar[./Identifier="{func_name}"]',
        )

    def find_decorators(self, dec_name):
        return self.xpath('.//Directive[./UnbracedExpression="%s"]' % dec_name)

    def get_enclosing_blocks(self):
        """
        Get the nodes representing the blocks that enclose this node.
        """
        # TODO: unit test, with decorators
        return self.xpath(
            # Grab directives that are our direct ancestor.
            './ancestor::Directive'
            '|'  # OR:
            # Look at all ancestors.
            './ancestor::*'
            # Its last child element should be an #end Directive
            '[./*[last()][self::Directive][starts-with(., "#end")]]'
            # Grab the first child. Require that it's a directive
            '/*[1][self::Directive]'
            # Use the first directive that's not a Decorator.
            '/descendant-or-self::Directive[not(./Decorator)]'
        )

    def add_comment(self, comment_text):
        text = self.find_indent_textnode()
        try:
            before, after = text.rsplit('\n', 1)
            before += '\n'
        except ValueError:
            before, after = '', text
        # Now the comment would be flush to the left-hand margin.
        indent = after.replace(after.lstrip(), '')  # Get just the whitespace.
        before += indent
        after = '\n' + after

        parent = text.getparent()
        comment = self.make_comment(comment_text)

        if text.is_text:
            parent.text = before
            parent.insert(0, comment)
            comment.tail = after
        else:  # text.is_tail
            parent.addnext(comment)
            parent.tail, comment.tail = before, after

    def make_comment(self, comment_text):
        comment = self.makeelement('Comment')
        comment_start = self.makeelement('CommentStart')
        comment_start.text = '##'
        comment_start.tail = ' ' + comment_text

        comment.append(comment_start)
        return comment

    def is_in_context(self, directive_string):
        if isinstance(directive_string, bytes):
            directive_string = directive_string.decode('UTF-8')
        try:
            directive_name, var = directive_string.split(None, 1)
        except ValueError:
            directive_name, var = directive_string.strip(), None

        directive_name = directive_name.lstrip('#')
        root = self.getroottree().getroot()

        for directive in self.get_enclosing_blocks():
            if (
                    # TODO: create a Directive and simply compare
                    directive.name == directive_name and
                    (
                        directive.var is None and var is None or
                        directive.var.totext(with_tail=False).decode('UTF-8') == var
                    )
            ):
                return True

            if directive.name == 'def':
                func = directive.var.totext(with_tail=False)
                for call in root.find_calls(func):
                    if directive in call.get_enclosing_blocks():
                        # Don't try to analyze recursion
                        # TODO: handle loops: f() -> g() -> h() -> f()
                        # TODO: add unit test for this case.
                        continue
                    elif call.is_in_context(directive_string):
                        return True
        else:
            return False

    def call(self, method, arguments):
        """
        return an lxml node representing a call to a method, with arguments.
        `method` is a string
        `arguments` is an lxml node
        """
        call = self.makeelement('Placeholder')
        call.text = '$'

        identifier = self.makeelement('Identifier')
        identifier.text = method
        call.append(identifier)

        call_expr = self.makeelement('BracedExpression')
        start_py = self.makeelement('Py')
        start_py.text = '('
        call_expr.append(start_py)
        call_expr.append(arguments)
        end_py = self.makeelement('Py')
        end_py.text = ')'
        call_expr.append(end_py)
        call.append(call_expr)

        return call


class CheetahVariable(CheetahNodeBase):
    """
    This class represents a cheetah placeholder, such as: $FOO
    """

    @property
    def name(self):
        return one(self.xpath('./Identifier'))

    @property
    def args_container(self):
        return one(self.xpath('BracedExpression'))

    @property
    def args(self):
        args = self.args_container.getchildren()
        assert args[0].tag == 'Py' and args[0].text == '('
        assert args[-1].tag == 'Py' and args[-1].text == ')'
        args = args[1:-1]
        args = [arg for arg in args if arg.text.strip() or arg.tail.strip()]
        return args

    def remove_call(self):
        args = self.args

        if not args:
            self.remove_self()
        elif len(args) == 1 and args[0].tag == 'CheetahVar':
            self.replace_self(args[0])
        elif (
                len(args) == 1 and
                args[0].tag == 'Py' and
                args[0].text.startswith(('"', "'"))
        ):
            # A single string argument
            if self.is_top_level:
                new_element = self.makeelement('PlainText')
                new_element.text = args[0].text
                if new_element.text.startswith(('"' * 3, "'" * 3)):
                    new_element.text = new_element.text[3:-3]
                else:
                    new_element.text = new_element.text[1:-1]
            else:
                new_element = args[0]

            new_element.tail = self.tail
            self.replace_self(new_element)
        elif self.is_top_level:
            # Something else, wrap it in braces and call it good
            new_element = self.makeelement('Placeholder')
            new_element.text = '${'
            args[-1].tail += '}'
            new_element.extend(args)
            new_element.tail = self.tail
            self.replace_self(new_element)
        else:
            # Replace inline
            new_element = self.makeelement('Unknown')
            new_element.extend(args)
            new_element.tail = self.tail
            self.replace_self(new_element)


class CheetahPlaceholder(CheetahVariable):
    is_top_level = True


class CheetahVar(CheetahVariable):
    is_top_level = False


class CheetahDirective(CheetahNodeBase):
    def replace_directive(self, other):
        if isinstance(other, str):
            var = self.makeelement('CheetahVar')
            try:
                directive, var.text = other.split(None, 1)
            except ValueError:
                directive, var.text = other.strip(), ''
            directive = directive.lstrip('#')
        else:
            raise NotImplementedError("Patches Are Welcome!")
            directive = other.name
            var = other.xpath('.//CheetahVar')[0]

        self.name = directive
        self.var = var

        if self.is_multiline_directive:
            # Multi-line form: Need to update the end directive.
            end_expression = self.get_end_directive().xpath_one('./UnbracedExpression')
            tail = end_expression.tail
            end_expression.clear()
            end_expression.text = directive
            end_expression.tail = tail

    @property
    def is_multiline_directive(self):
        return (
            self.totext().strip().endswith(b':') or
            not self.xpath(
                './self::Directive[starts-with(., "#end")] or '
                './SimpleExprDirective or '
                './/text()="):" or '
                './/text()=":"'
            )
        )

    @property
    def DirectiveStart(self):
        return self.xpath_one(
            './DirectiveStart[1] |  ./SimpleExprDirective/DirectiveStart[1]'
        )

    def __get_name(self):
        "The name of the directive. The word just after the first # sign."
        return self.DirectiveStart.tail.rstrip()

    def __set_name(self, val):
        dstart = self.DirectiveStart
        padding = dstart.tail.replace(dstart.tail.rstrip(), '')
        dstart.tail = val + padding

    name = property(__get_name, __set_name)

    def __get_var(self):
        try:
            return self.xpath_one('./*/CheetahVar | ./Identifier')
        except ValueError:
            return None

    def __set_var(self, var):
        old_var = self.var

        if old_var is None:
            self.append(var)
        else:
            var.tail = old_var.tail
            old_var.replace_self(var)

    var = property(__get_var, __set_var)

    def get_end_directive(self):
        """Returns the #end Directive node that logically matches this
        Directive.
        """
        # Look at sibling Directives after this node, take first one that is
        # an #end Directive.
        return self.xpath_one('./following-sibling::Directive[starts-with(., "#end")]')


class NodeLookup(etree.PythonElementClassLookup):
    """
    Specify how to assign Python classes to lxml objects.
    see: http://lxml.de/element_classes.html#tree-based-element-class-lookup-in-python
    """

    def lookup(self, document, element):
        if element.tag == 'Placeholder':
            return CheetahPlaceholder
        elif element.tag == 'CheetahVar':
            return CheetahVar
        elif element.tag == 'Directive':
            return CheetahDirective
        else:
            return CheetahNodeBase


node_lookup = NodeLookup()
del NodeLookup  # This is a singleton class.
