import gettext
_ = gettext.gettext

from BeautifulSoup import BeautifulSoup, Declaration, Comment, Tag

import _base

class TreeWalker(_base.TreeWalker):
    def __init__(self, node):
        self.node = node

    def _getType(self):
        node = self.node
        if isinstance(node, BeautifulSoup): # Document or DocumentFragment
            return "DocumentFragment"

        elif isinstance(node, Declaration):
            return "Doctype"

        elif isinstance(node, Comment):
            return "Comment"

        elif isinstance(node, unicode):
            return "Text"

        elif isinstance(node, Tag):
            return "Element"

        else:
            raise TypeError("Are there other types?")

    def _getName(self):
        node = self.node
        if isinstance(node, Declaration):
            #Slice needed to remove markup added during unicode conversion
            return unicode(node.string)[2:-1]

        assert isinstance(node, Tag)
        return node.name

    def _getValue(self):
        node = self.node
        if isinstance(node, Comment):
            #Slice needed to remove markup added during unicode conversion
            return unicode(node.string)[4:-3]

        assert isinstance(node, unicode)
        return node

    def _getAttributes(self):
        node = self.node
        assert isinstance(node, Tag)
        return tuple(dict(node.attrs).items())

    def _hasChildren(self):
        node = self.node
        assert isinstance(node, Tag)
        return bool(node.contents)

    def firstChild(self):
        self.node = self.node.contents[0]

    def nextSibling(self):
        if self.node.nextSibling:
            self.node = self.node.nextSibling
            return True
        else:
            return False

    def parentNode(self):
        return self.node.parent
