from refactorlib.dictnode import set_node_text
from Cheetah.legacy_compiler import LegacyCompiler
from Cheetah.legacy_parser import LegacyParser


DEBUG = False


class InstrumentedMethod:
    def __init__(self, method, parent, name=None):
        self.method = method
        self.parent = parent
        self.name = name or method.__name__

    def __call__(self, *args, **kwargs):
        # I want the data to be arranged in *call* order
        start_pos = self.parent.pos()

        mydata = [start_pos, None, self.name]
        self.parent.data.append(mydata)
        result = self.method(*args, **kwargs)  # Call the wrapped method.
        mydata[1] = self.parent.pos()

        return result


class InstrumentedParser(LegacyParser):
    dont_care_methods = (
        'getc', 'getRowCol', 'getRowColLine', 'get_placeholder_expression',
    )
    translate_method_names = {
        '_read_cheetah_variable_with_dollarsign': 'CheetahVar',
        '_read_braced_expression': 'BracedExpression',
        'get_unbraced_expression': 'UnbracedExpression',
        'get_def_argspec': 'DefArgspec',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = []
        self._openDirectivesDataStack = []

        # Add instrumentation to certain methods
        for attr in dir(self):
            val = getattr(self, attr)
            method = self.instrument_method(val)
            if method is not None:
                setattr(self, attr, method)

    def instrument_method(self, method):
        from types import MethodType
        if not isinstance(method, MethodType):
            return
        name = method.__name__
        if name in self.dont_care_methods:
            return
        elif name in self.translate_method_names:
            return InstrumentedMethod(
                method, self,
                name=self.translate_method_names[name],
            )
        elif name.startswith('eat') or name.startswith('get'):
            return InstrumentedMethod(method, self)

    def pushToOpenDirectivesStack(self, directive_name):
        result = super().pushToOpenDirectivesStack(directive_name)

        # This properly goes just before the previous eatDirective
        for i, (start, end, name) in enumerate(reversed(self.data), 1):
            if name == 'eatDirective':
                break

        index = len(self.data) - i
        self._openDirectivesDataStack.append((index, start))

        return result

    def popFromOpenDirectivesStack(self, directive_name, **kwargs):
        result = super().popFromOpenDirectivesStack(directive_name, **kwargs)

        directive_index, mystart = self._openDirectivesDataStack.pop()
        myend = self.pos()

        # Have to check for children that started before eatDirective (e.g. decorators)
        myindex = directive_index
        for i, (start, end, name) in enumerate(reversed(self.data[:directive_index]), 1):
            if start <= mystart and mystart < end < myend:
                mystart = min(start, mystart)
                myindex = directive_index - i

        data = [mystart, myend, directive_name]
        self.data.insert(myindex, data)

        return result


# This is very screwy, but so is cheetah. Apologies.
class InstrumentedCompiler(LegacyCompiler):
    parserClass = InstrumentedParser


def detect_encoding(source):
    # Cheetah source is invariantly utf-8
    return 'UTF-8'


def parse(cheetah_content, encoding=None):
    # yelp_cheetah requires text
    if type(cheetah_content) is bytes:
        cheetah_content = cheetah_content.decode('UTF-8')

    compiler = InstrumentedCompiler(cheetah_content)
    compiler.getModuleCode()
    data = compiler._parser.data

    if DEBUG:
        data = show_data(data, cheetah_content)
    data = nice_names(data)
    data = remove_empty(data)
    data = dedup(data)

    dictnode = parser_data_to_dictnode(data, cheetah_content)

    from refactorlib.parse import dictnode_to_lxml
    from refactorlib.cheetah.node import node_lookup
    root = dictnode_to_lxml(dictnode, node_lookup, encoding)
    return root


def remove_empty(data):
    for datum in data:
        start, end, method = datum
        if start != end:
            yield datum


def show_data(data, src):  # pragma: no cover (debug)
    for datum in data:
        start, end, method = datum
        print(method, repr(src[start:end]), start, end)
        yield datum


def nice_names(data):
    for start, end, method in data:
        yield start, end, method_to_tag(method)


def parser_data_to_dictnode(data, src):
    root = dict(name='cheetah', start=0, end=len(src) + 1, text='', tail='', attrs={}, children=[])
    stack = [root]

    for datum in data:
        start, end, name = datum
        dictnode = dict(name=name, start=start, end=end, text='', tail='', attrs={}, children=[])

        parent = stack[-1]
        while parent['end'] < end:
            if parent['end'] <= start:
                # That's proper
                set_node_text(stack.pop(), src)
                parent = stack[-1]
            else:
                # That guy used backtracking! Remove him.
                # This complements, but doesn't replace, the dedup() function,
                # since backtracking functions won't necessarily fail this test
                badguy = stack.pop()
                parent = stack[-1]
                parent['children'].remove(badguy)
                if DEBUG:
                    print('Removed bad:', badguy)

        parent['children'].append(dictnode)
        stack.append(dictnode)

    # clean up
    while stack:
        set_node_text(stack.pop(), src)

    return root


def dedup(data):
    """Cheetah occasionally backtracks and produces identical calls.
    TODO: factor this out upstream: Yelp/yelp_cheetah#234
    """
    new_data = []  # Can't yield. We need to look behind.
    file_pointer = 0
    for datum in data:
        start, end, name = datum

        if start > file_pointer:
            # New data.
            file_pointer = start
            new_data.append(datum)
            continue

        dup_index = None
        for i, d in enumerate(reversed(new_data)):
            if d == datum:
                dup_index = -1 - i
                break
            elif d[0] < start:
                break

        if dup_index is None:
            new_data.append(datum)
        elif file_pointer == start:
            # Dupe: This is a simple backtrack, take the latest parsing.
            if DEBUG:
                print("Duped:", datum)
            del new_data[dup_index]
            new_data.append(datum)
        else:
            # Dupe: We've advanced beyond this data, drop it.
            if DEBUG:
                print("Dropped:", datum)
            pass
    return new_data


def method_to_tag(methodname):
    if methodname.startswith('eat') or methodname.startswith('get'):
        tagname = methodname[3:]
    else:
        tagname = methodname

    if tagname.endswith('Token'):
        tagname = tagname[:-5]

    return tagname
