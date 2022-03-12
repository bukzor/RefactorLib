"""A few functions for dealing with the "dictnode" intermediate tree format."""


class DictNode(dict):
    __slots__ = ()

    def __str__(self):
        return '{}({}-{})'.format(self['name'], self['start'], self['end'])


def set_node_text(dictnode, src):
    """
    Given a single dictnode and source code, fill in its 'text' attribute properly.
    The 'tail' of the children is filled in where appropriate.
    The node and its children must have a 'start' and 'end' integer property.

    Run this function on every node in the tree to completely fill out text and tail.
    """
    my = dictnode
    if my['children']:
        # my text is between my start and the first child's start
        child = my['children'][0]
        my['text'] = src[my['start']:child['start']]

        # each child's tail is between their end and the next child's start
        for next_child in my['children'][1:]:
            child['tail'] = src[child['end']:next_child['start']]
            child = next_child  # The old next is the new current

        # except the last child's tail is between its end and my end
        child = my['children'][-1]
        child['tail'] = src[child['end']:my['end']]
    else:
        # If if I have no children, my text is just between my start and end
        my['text'] = src[my['start']:my['end']]


def set_tree_text(dictnode_tree, src):
    """
    We do a pre-order traversal of the tree to calculate the text and tail
    of each node
    """
    # We *could* jam this into the dictnode function, but this is simpler.
    tree = dictnode_tree
    stack = [tree]
    while stack:
        node = stack.pop()
        set_node_text(node, src)
        stack.extend(reversed(node['children']))

    # The top-level node cannot have a tail
    assert not tree.get('tail')
    tree['tail'] = None
    return tree
