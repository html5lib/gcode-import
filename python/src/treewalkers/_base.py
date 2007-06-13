
class TreeWalker(object):
    def _getType(self):
        raise NotImplementedError
    type = property(lambda self: self._getType(), doc= \
        """Read-only. A string, either "Document", "DocumentFragment", "Doctype",
        "Element", "Text" or "Comment".
        """)

    def _getName(self):
        raise NotImplementedError
    name = property(lambda self: self._getName(), doc= \
        """Read-only. The current node's name.

        Valid only if type is "Doctype" or "Element".
        """)

    def _getAttributes(self):
        raise NotImplementedError
    attributes = property(lambda self: self._getAttributes(), doc= \
        """Read-only. A tuple of (name, value) tuples representing the \
        current node's attributes.

        Valid only if type is "Element"
        """)

    def _getValue(self):
        raise NotImplementedError
    value = property(lambda self: self._getValue(), doc= \
        """Read-only. The current node's value.

        Valid only if type is "Text" or "Comment".
        """)

    def _hasChildren(self):
        raise NotImplementedError
    hasChildren = property(lambda self: self._hasChildren(), doc= \
        """Read-only. A boolean telling whether the current node has children.

        Valid only if type is "Document", "DocumentFragment" or "Element".
        """)

    def firstChild(self):
        """Move to the current node's first child.

        This method is called only if type is "Document", "DocumentFragment" or "Element"
        and if hasChildren is True.
        """
        raise NotImplementedError

    def nextSibling(self):
        """Move to the current node's next sibling and return True, or return False if there are no following siblings."""
        raise NotImplementedError

    def parentNode(self):
        """Move to the current node's parent.

        This method is never called if type is "Document" or "DocumentFragment"
        """
        raise NotImplementedError

