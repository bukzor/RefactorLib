"""
Some basic additions to the lxml element node class.
"""
from lxml import etree


class RefactorLibNodeBase(etree.ElementBase):
    @property
    def encoding(self):
        # My encoding is the encoding of my root, if any
        return self.getroottree().docinfo.encoding

    def remove_call(self):
        raise NotImplementedError('remove_call')

    def replace_self(self, other):
        parent = self.getparent()
        parent.replace(self, other)

    def remove_self(self):
        parent = self.getparent()
        parent.remove(self)

    def totext(self, encoding=None, with_tail=True, **kwargs):
        if encoding is None:
            encoding = self.encoding
        return etree.tostring(self, encoding=encoding, method='text', with_tail=with_tail, **kwargs)

    def tostring(self, encoding=None, method=None, with_tail=True, **kwargs):
        if encoding is None:
            encoding = self.encoding
        return etree.tostring(self, encoding=encoding, method=method, with_tail=with_tail, **kwargs)

    def following_text(self):
        """
        Get the first non-empty piece of text after this node.
        See also: http://lxml.de/tutorial.html#using-xpath-to-find-text
        """
        return one(self.xpath('./following::text()[.!=""][1]'))

    def preceding_text(self):
        """
        Get the first non-empty piece of text before this node.
        See also: http://lxml.de/tutorial.html#using-xpath-to-find-text
        """
        return one(self.xpath('./preceding::text()[.!=""][1]'))

    def clear_indent(self):
        """
        Clear any indent preceding this node.
        """
        indent = self.preceding_text()
        attr = 'text' if indent.is_text else 'tail'
        indent_owner = indent.getparent()
        setattr(indent_owner, attr, indent.rstrip(' \t'))

    def find_indent_textnode(self):
        """
        Find and return the raw text node that includes the indentation for
        this node. Other, non-whitespace charcters may be included.
        """
        text = self.preceding_text()
        while '\n' not in text:
            prevnode = text.getparent()
            prevnode_preceding = prevnode.preceding_text()
            if (
                    prevnode.text.endswith('\n') or
                    prevnode_preceding.endswith('\n')
            ):
                break
            else:
                text = prevnode_preceding

        return text

    def xpath_one(self, xpath):
        return one(self.xpath(xpath))

    def __nonzero__(self):
        """
        Nodes should always test True.
        This is forward-compatible with the newest lxml version.
        """
        return True


class ExactlyOneError(ValueError):
    pass


def one(mylist):
    """
    assert that there's only one thing, and get it.
    """
    if len(mylist) != 1:
        raise ExactlyOneError(
            'Expected exactly one item. Got %i: %r' % (
                len(mylist),
                [
                    item.tostring()
                    if isinstance(item, etree.ElementBase)
                    else item
                    for item in mylist
                ]
            )
        )

    return mylist[0]


node_lookup = etree.ElementDefaultClassLookup(element=RefactorLibNodeBase)

__all__ = ('RefactorLibNodeBase',)
