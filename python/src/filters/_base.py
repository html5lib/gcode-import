from treewalkers._base import TreeWalker

class Filter(TreeWalker):
    def __init__(self, source):
        self.source = source

    type = property(lambda self: self.source.type, \
        doc=TreeWalker.type.__doc__)
    name = property(lambda self: self.source.name, \
        doc=TreeWalker.name.__doc__)
    value = property(lambda self: self.source.value, \
        doc=TreeWalker.value.__doc__)
    attributes = property(lambda self: self.source.attributes, \
        doc=TreeWalker.attributes.__doc__)
    hasChildren = property(lambda self: self.source.hasChildren, \
        doc=TreeWalker.hasChildren.__doc__)

    def firstChild(self):
        self.source.firstChild()
    firstChild.__doc__ = TreeWalker.firstChild.__doc__

    def nextSibling(self):
        return self.source.nextSibling()
    nextSibling.__doc__ = TreeWalker.nextSibling.__doc__

    def parentNode(self):
        self.source.parentNode()
    parentNode.__doc__ = TreeWalker.parentNode.__doc__
