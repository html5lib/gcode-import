from lxml import etree

import _base

class TreeWalker(_base.TreeWalker):
    def __init__(self, tree):
        if not hasattr(tree, 'tag'):
            tree = tree.getroot()
        self.startNode = tree
        self.currentNode = tree
        self.extra = None # None, 'text' or 'tail'

    def _getType(self):
        if self.extra is not None:
            return "Text"
        elif self.currentNode is self.startNode:
            return "DocumentFragment"
        elif self.currentNode.tag == etree.Comment:
            return "Comment"
        elif self.currentNode.tag == "<!DOCTYPE>":
            return "Doctype"
        else:
            return "Element"

    type = property(_getType)

    name = property(lambda self: self.currentNode.tag == "<!DOCTYPE>" and self.currentNode.text or self.currentNode.tag)

    attributes = property(lambda self: tuple(self.currentNode.items()))

    value = property(lambda self: getattr(self.currentNode, self.extra or 'text'))

    hasChildren = property(lambda self: bool(self.currentNode or self.currentNode.text))

    def firstChild(self):
        if self.currentNode.text:
            self.extra = 'text'
        else:
            assert not self.extra
            self.extra = None
            self.currentNode = self.currentNode[0]

    def nextSibling(self):
        if not self.extra and self.currentNode.tail:
            self.extra = 'tail'
        elif self.extra == 'text':
            if self.currentNode:
                self.extra = None
                self.currentNode = self.currentNode[0]
                return True
            else:
                return False
        else:
            self.extra = None
            next = self.currentNode.getnext()
            if next is not None:
                self.currentNode = next
                return True
            else:
                return False

    def parentNode(self):
        if self.extra == 'text':
            self.extra = None
        else:
            self.currentNode = self.currentNode.getparent()
