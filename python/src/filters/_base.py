from treewalkers._base import TreeWalker

class Filter(TreeWalker):
    def __init__(self, source):
        self.source = source

    def _getType(self):
        return self.source.type
    def _getName(self):
        return self.source.name
    def _getValue(self):
        return self.source.value
    def _getAttributes(self):
        return self.source.attributes
    def _hasChildren(self):
        return self.source.hasChildren

    def firstChild(self):
        self.source.firstChild()
    firstChild.__doc__ = TreeWalker.firstChild.__doc__

    def nextSibling(self):
        return self.source.nextSibling()
    nextSibling.__doc__ = TreeWalker.nextSibling.__doc__

    def parentNode(self):
        self.source.parentNode()
    parentNode.__doc__ = TreeWalker.parentNode.__doc__
