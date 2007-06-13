from xml.dom import Node

import gettext
_ = gettext.gettext

import _base

class TreeWalker(_base.TreeWalker):
    def __init__(self, node):
        self.node = node

    def _getType(self):
        node = self.node

        if node.nodeType == Node.DOCUMENT_TYPE_NODE:
            return "Doctype"

        elif node.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
            return "Text"

        elif node.nodeType == Node.ELEMENT_NODE:
            return "Element"

        elif node.nodeType == Node.COMMENT_NODE:
            return "Comment"

        elif node.nodeType == Node.DOCUMENT_NODE:
            return "Document"

        elif node.nodeType == Node.DOCUMENT_FRAGMENT_NODE:
            return "DocumentFragment"

        else:
            raise Exception("What to do with PIs and other nodes?")

    def _getName(self):
        return self.node.nodeName

    def _getValue(self):
        return self.node.nodeValue

    def _getAttributes(self):
        return tuple(self.node.attributes.items())

    def _hasChildren(self):
        return self.node.hasChildNodes()

    def firstChild(self):
        self.node = self.node.firstChild

    def nextSibling(self):
        node = self.node.nextSibling
        if node is not None:
            self.node = node
            return True
        else:
            return False

    def parentNode(self):
        self.node = self.node.parentNode
