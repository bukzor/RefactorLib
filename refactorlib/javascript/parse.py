from json import loads

from refactorlib.util import static


DEBUG = False


def parse(javascript_contents, encoding='ascii'):
    """Given some javascript contents, as a text string, return the lxml representation.
    "reflectjs" below refers to the Mozilla Reflect protocol:
        * https://developer.mozilla.org/en-US/docs/SpiderMonkey/Parser_API
        * https://npmjs.org/package/reflect
    """
    from refactorlib.dictnode import set_tree_text
    reflectjs_javascript = reflectjs_parse(javascript_contents)
    dictnode_javascript = reflectjs_to_dictnode(reflectjs_javascript)
    dictnode_javascript = set_tree_text(dictnode_javascript, javascript_contents)

    from refactorlib.parse import dictnode_to_lxml
    return dictnode_to_lxml(dictnode_javascript, encoding=encoding)


@static(found=False)
def find_nodejs():
    if find_nodejs.found is False:
        from refactorlib.util import which
        nodejs = which('nodejs')
        if nodejs is None:
            nodejs = which('node')
        find_nodejs.found = nodejs
    return find_nodejs.found


def reflectjs_parse(javascript_contents):
    from refactorlib import TOP
    from refactorlib.util import Popen, PIPE
    from os.path import join
    from collections import OrderedDict
    reflectjs_script = join(TOP, 'javascript/reflectjs.js')

    reflectjs = Popen([find_nodejs(), reflectjs_script], stdin=PIPE, stdout=PIPE)
    json = reflectjs.check_output(javascript_contents)
    tree = loads(json, object_pairs_hook=OrderedDict)

    # reflectjs is sometimes neglectful of leading/trailing whitespace.
    tree['range'] = [0, len(javascript_contents)]

    return tree


def reflectjs_to_dictnode(tree):
    """
    Transform a reflectjs structure into a dictnode, as defined by dictnode_to_lxml.
    This is not a complete transformation. In particular, the nodes have no
    text or tail, and may have some overlap issues.
    """
    from refactorlib.dictnode import DictNode

    root_dictnode = DictNode(parent=None)
    stack = [(tree, root_dictnode)]

    while stack:
        node, dictnode = stack.pop()

        children = []
        attrs = {}
        for attr, val in node.items():
            if attr in ('loc', 'type', 'range'):
                # These are handled more directly, below.
                continue
            elif isinstance(val, list):
                children.extend(val)
            elif isinstance(val, dict) and 'loc' in val:
                if val.get('loc'):
                    children.append(val)
                else:
                    attrs[val['type']] = val['name']
            elif attr == 'value':
                attrs[attr] = str(val)
                # We would normally lose this type information, as lxml
                # wants everything to be a string.
                attrs['type'] = type(val).__name__
            elif isinstance(val, str):
                attrs[attr] = val
            elif isinstance(val, bytes):
                attrs[attr] = val.decode('UTF-8')
            elif isinstance(val, (bool, type(None))):
                # TODO: figure out what happens with non-ascii data.
                attrs[attr] = str(val)
            else:  # Should never happen
                assert False

        dictnode.update(dict(
            name=node['type'],
            start=node['range'][0],
            end=node['range'][1],
            children=[DictNode(parent=dictnode) for child in children],
            attrs=attrs,
        ))
        stack.extend(reversed(list(zip(children, dictnode['children']))))
    return root_dictnode
