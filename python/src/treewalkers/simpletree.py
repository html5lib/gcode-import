import gettext
_ = gettext.gettext

import _base

class TreeWalker(_base.TreeWalker):
    """Given that simpletree has no performant way of getting a node's
    next sibling, this implementation returns "nodes" as tuples with the
    following content:

    1. The parent Node (Element, Document or DocumentFragment)

    2. The child index of the current node in its parent's children list

    3. A list used as a stack of all ancestors. It is a pair tuple whose
       first item is a parent Node and second item is a child index.
    """

    def __init__(self, node):
        self.node = node

    def _getNode(self):
        node = self.node
        if isinstance(node, tuple):
            parent, idx, parents = node
            node = parent.childNodes[idx]
        return node

    def _getType(self):
        node = self._getNode()

        # testing node.type allows us not to import treebuilders.simpletree
        if node.type == 1:
            return "Document"

        elif node.type == 2:
            return "DocumentFragment"

        elif node.type == 3:
            return "Doctype"

        elif node.type == 4:
            return "Text"

        elif node.type == 5:
            return "Element"

        elif node.type == 6:
            return "Comment"

        else:
            raise Exception("Are there other types?")

    def _getName(self):
        return self._getNode().name

    def _getValue(self):
        node = self._getNode()
        if node.type == 6: # Comment
            return node.data
        return node.value

    def _getAttributes(self):
        return tuple(self._getNode().attributes.items())

    def _hasChildren(self):
        return self._getNode().hasContent()

    def firstChild(self):
        node = self.node
        if isinstance(node, tuple):
            parent, idx, parents = node
            parents.append((parent, idx))
            node = parent.childNodes[idx]
        else:
            parents = []

        assert node.hasContent(), "Node has no children"
        self.node = (node, 0, parents)

    def nextSibling(self):
        assert isinstance(self.node, tuple), "Node is not a tuple: " + str(node)
        parent, idx, parents = self.node
        idx += 1
        if len(parent.childNodes) > idx:
            self.node = (parent, idx, parents)
            return True
        else:
            return False

    def parentNode(self):
        assert isinstance(self.node, tuple)
        parent, idx, parents = self.node
        if parents:
            parent, idx = parents.pop()
            self.node = parent, idx, parents
        else:
            self.node = parent
