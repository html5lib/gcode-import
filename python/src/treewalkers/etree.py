import gettext
_ = gettext.gettext

import new

import _base
from constants import voidElements

moduleCache = {}

def getETreeModule(ElementTreeImplementation):
    name = "_" + ElementTreeImplementation.__name__+"builder"
    if name in moduleCache:
        return moduleCache[name]
    else:
        mod = new.module("_" + ElementTreeImplementation.__name__+"builder")
        objs = getETreeBuilder(ElementTreeImplementation)
        mod.__dict__.update(objs)
        moduleCache[name] = mod
        return mod

def getETreeBuilder(ElementTreeImplementation):
    ElementTree = ElementTreeImplementation

    _tag2type = {
        "<DOCUMENT_ROOT>": "Document",
        "<DOCUMENT_FRAGMENT>": "DocumentFragment",
        "<!DOCTYPE>": "Doctype",
        ElementTree.Comment: "Comment",
    }

    class TreeWalker(_base.TreeWalker):
        """Given the particular ElementTree representation, this implementation,
        to avoid using recursion, returns "nodes" as tuples with the following
        content:

        1. An Element node serving as *context* (it cannot be called the parent
           node due to the particular ``tail`` text nodes.

        2. Either the string literals ``"text"`` or ``"tail"`` or a child index

        3. A list used as a stack of all ancestor *context nodes*. It is a
           pair tuple whose first item is an Element and second item is a child
           index.

        Note that there is a TreeWalker taking advantage of lxml.etree internal
        representation and specific API in html5lib.treewalkers.lxmletree.
        """

        def __init__(self, node):
            if not hasattr(node, 'tag'):
                node = node.getroot()
            self.node = node

        def _getType(self):
            node = self.node
            if isinstance(node, tuple):
                elt, key, parents = node
                if key in ("text", "tail"):
                    return "Text"
                else:
                    node = elt[int(key)]
            return _tag2type.get(node.tag, "Element")

        def _getName(self):
            node = self.node
            if isinstance(node, tuple):
                elt, key, parents = node
                assert key not in ("text", "tail")
                node = elt[int(key)]
            if node.tag == "<!DOCTYPE>":
                return node.text
            return node.tag

        def _getValue(self):
            node = self.node
            if isinstance(node, tuple):
                elt, key, parents = node
                if key in ("text", "tail"):
                    return getattr(elt, key)
                else:
                    node = elt[int(key)]
            assert node.tag == ElementTree.Comment
            return node.text

        def _getAttributes(self):
            node = self.node
            if isinstance(node, tuple):
                elt, key, parents = node
                assert key not in ("text", "tail")
                node = elt[int(key)]
            assert node.tag not in _tag2type
            return tuple(node.items())

        def _hasChildren(self):
            node = self.node
            if isinstance(node, tuple):
                elt, key, parents = node
                assert key not in ("text", "tail")
                node = elt[int(key)]
            assert node.tag not in ("<!DOCTYPE>", ElementTree.Comment)
            return len(node) or node.text

        def firstChild(self):
            node = self.node
            if isinstance(node, tuple):
                elt, key, parents = node
                assert key not in ("text", "tail"), "Text nodes have no children"
                parents.append((elt, int(key)))
                node = elt[int(key)]
            else:
                parents = []

            assert len(node) or node.text, "Node has no children"
            self.node = (node, node.text and "text" or 0, parents)

        def nextSibling(self):
            assert isinstance(self.node, tuple), "Node is not a tuple: " + str(node)

            elt, key, parents = self.node
            if key == "text":
                key = -1
            elif key == "tail":
                elt, key = parents.pop()
            else:
                # Look for "tail" of the "revisited" node
                child = elt[key]
                if child.tail:
                    parents.append((elt, key))
                    self.node = (child, "tail", parents)
                    return True

            # case where key were "text" or "tail" or elt[key] had a tail
            key += 1
            if len(elt) > key:
                self.node = (elt, key, parents)
                return True
            else:
                return False

        def parentNode(self):
            assert isinstance(self.node, tuple)
            elt, key, parents = self.node
            if parents:
                elt, key = parents.pop()
                self.node = (elt, key, parents)
            else:
                self.node = elt

    return locals()
