import _base

from constants import spaceCharacters
spaceCharacters = u"".join(spaceCharacters)

class Filter(_base.Filter):
    def __init__(self, source, encoding=None):
        _base.Filter.__init__(self, source)
        self.encoding = unicode(encoding)
        # don't inject <meta charset> if there's no encoding
        self.inject_state = encoding and 'todo' or 'done'

    type = property(lambda self: self.inject_state == 'injecting' and "Element" or self.source.type)
    name = property(lambda self: self.inject_state == 'injecting' and u"meta" or self.source.name)

    def _getAttributes(self):
        """Return current node's attributes, removing any charset attribute
        (or every attributes if there is an http-equiv attribute with the
        value content-type) from <meta> elements.
        """
        if self.inject_state == 'injecting':
            return ((u"charset", self.encoding), )

        attrs = self.source.attributes
        if self.name.lower() == "meta":
            if filter(lambda attr: \
              map(lambda s: s.lower().strip(spaceCharacters), attr) == ("http-equiv", "content-type"),
              attr):
                attrs = tuple()
            else:
                attrs = ((name, value) for name, value in attrs if name.lower().strip(spaceCharacters) != "charset")
        return attrs
    attributes = property(_getAttributes)

    def _hasChildren(self):
        """Ensure <head> says it has child nodes if <meta charset> has to be injected."""
        if self.inject_state == 'todo' and self.name.lower() == "head":
            return True
        elif self.inject_state == 'injecting':
            return False
        return self.source.hasChildren
    hasChildren = property(_hasChildren)

    def firstChild(self):
        if self.inject_state == 'todo'and self.source.name.lower() == "head":
            # inject <meta charset>
            self.inject_state = 'injecting'
        else:
            self.source.firstChild()

    def nextSibling(self):
        if self.inject_state == 'injecting' and self.source.name.lower() == "head":
            if self.source.hasChildren:
                self.inject_state = 'done'
                self.source.firstChild()
                return True
            else:
                return False
        return self.source.nextSibling()

    def parentNode(self):
        if self.inject_state == 'injecting' and self.source.name.lower() == "head":
            self.inject_state = 'done'
            # If we're here, it means we've "emulated" the fact that <head>
            # has a <meta charset> child (i.e. <head> hadn't children). This
            # means we're still on the <head> element, so we just don't do
            # nothing.
        else:
            self.source.parentNode()
