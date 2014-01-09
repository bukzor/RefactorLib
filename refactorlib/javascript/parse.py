from refactorlib.util import static

DEBUG = False

def parse(javascript_contents, encoding='ascii'):
    """
    Given some javascript contents, as a unicode string, return the lxml representation.
    "reflectjs" below refers to the Mozilla Reflect protocol:
        * https://developer.mozilla.org/en-US/docs/SpiderMonkey/Parser_API
        * https://npmjs.org/package/reflect
    """
    reflectjs_javascript = reflectjs_parse(javascript_contents)
    dictnode_javascript = reflectjs_to_dictnode(javascript_contents, reflectjs_javascript)
    dictnode_javascript = calculate_text(javascript_contents, dictnode_javascript)

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
    from simplejson import loads
    from simplejson.ordered_dict import OrderedDict
    reflectjs_script = join(TOP, 'javascript/reflectjs.js')

    reflectjs = Popen([find_nodejs(), reflectjs_script], stdin=PIPE, stdout=PIPE)
    json = reflectjs.check_output(javascript_contents)
    tree = loads(json, object_pairs_hook=OrderedDict)

    try:
        last_newline = javascript_contents.rindex('\n')
    except ValueError:
        last_newline = 0

    # reflectjs is sometimes neglectful of leading/trailing whitespace.
    tree['loc']['start']['line'] = 1
    tree['loc']['start']['column'] = 0
    tree['loc']['end']['line'] = javascript_contents.count('\n') + 1
    tree['loc']['end']['column'] = len(javascript_contents) - last_newline

    return tree

def calculate_text(contents, tree):
    """
    We do a pre+post order traversal of the tree to calculate the text and tail
    of each node
    """
    pre, post = 'pre', 'post'
    index = 0
    prev_node = DictNode(name='ROOT', start=0, end=-1)
    stack = [(tree, post), (tree, pre)]
    while stack:
        node, time = stack.pop()
        if time is pre:
            nextindex = node['start']
            if prev_node is node['parent']:
                # First child.
                target = 'text'
            else:
                # Finish up previous sibling
                target = 'tail'
    
            for child in reversed(node['children']):
                stack.extend( ((child, post), (child, pre)) )
        elif time is post:
            nextindex = node['end']
            if prev_node is node:
                # Node has no children.
                target = 'text'
            else:
                # Finish up after last child.
                target = 'tail'

        prev_node[target] = contents[index:nextindex]
        if DEBUG:
            print '%-4s %s' % (time, node)
            print '     %s.%s = %r' % (prev_node, target, prev_node[target])

        # Get ready for next iteration
        index = nextindex
        prev_node = node

    # The top-level node cannot have a tail
    assert not tree.get('tail')
    tree['tail'] = None
    return tree

class DictNode(dict):
    __slots__ = ()
    def __str__(self):
        return '%s(%s-%s)' % (self['name'], self['start'], self['end'])

def reflectjs_to_dictnode(javascript_contents, tree):
    """
    Transform a reflectjs structure into a dictnode, as defined by dictnode_to_lxml.
    This is not a complete transformation. In particular, the nodes have no
    text or tail, and may have some overlap issues.
    """
    from types import NoneType

    root_dictnode = DictNode(parent=None)
    stack = [(tree, root_dictnode)]
    lines = [len(line)+1 for line in javascript_contents.split('\n')]

    while stack:
        node, dictnode = stack.pop()
            
        children = []
        attrs = {}
        for attr, val in node.items():
            if attr in ('loc', 'type', 'range'):
                continue
            elif isinstance(val, list):
                children.extend(val)
            elif isinstance(val, dict) and 'loc' in val:
                if val.get('loc'):
                    children.append(val)
                else:
                    attrs[val['type']] = val['name']
            elif attr == 'value':
                attrs[attr] = unicode(val)
                # We would normally lose this type information, as lxml
                # wants everything to be a string.
                attrs['type'] = type(val).__name__
            elif isinstance(val, unicode):
                attrs[attr] = val
            elif isinstance(val, (bool, NoneType, str)):
                # TODO: figure out what happens with non-ascii data.
                attrs[attr] = unicode(val)
            else: # Should never happen
                import pudb; pudb.set_trace()

        dictnode.update(dict(
            name=node['type'],
            start=sum(lines[:node['loc']['start']['line']-1]) + node['loc']['start']['column'],
            end=sum(lines[:node['loc']['end']['line']-1]) + node['loc']['end']['column'],
            children=[DictNode(parent=dictnode) for child in children],
            attrs=attrs,
        ))
        stack.extend(reversed(zip(children, dictnode['children'])))
    return root_dictnode
