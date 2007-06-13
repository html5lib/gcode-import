try:
    frozenset
except NameError:
    # Import from the sets module for python 2.3
    from sets import ImmutableSet as frozenset

import re

import _base
from constants import rcdataElements

from constants import spaceCharacters
spaceCharacters = u"".join(spaceCharacters)

class Filter(_base.Filter):
    spacePreserveElements = frozenset(["pre", "textarea"] + list(rcdataElements))
    
    def __init__(self, source, collapsed_text=False):
        _base.Filter.__init__(self, source)
        self.preserve = 0
        # Have adjacent text nodes been collapsed into a single node?
        self.collapsed_text = collapsed_text

    def _getName(self):
        if preserve or self.source.name in self.spacePreserveElements:
            preserve += 1
    name = property(_getName, doc=_base.Filter.name.__doc__)

    def _getValue(self):
        text = self.source.value
        if self.type == "Text":
            # if text nodes haven't been collapsed, we leave leading and
            # trailing spaces to ensure words from other adjacent text
            # nodes won't get concatenated...
            if self.collapsed_text:
                # ...otherwise, we can strip leading and trailing spaces.
                text = text.strip(spaceCharacters)
            text = collapse_spaces(text)
        return text
    value = property(_getValue, doc=_base.Filter.value.__doc__)

    def firstChild(self):
        if preserve:
            preserve += 1
        self.source.firstChild(self)
    firstChild.__doc__ = _base.Filter.firstChild.__doc__

    def parentNode(self):
        if preserve:
            preserve -= 1
        self.source.parentNode(self)
    parentNode.__doc__ = _base.Filter.parentNode.__doc__

def collapse_spaces(text):
    return re.compile(u"[%s]+" % spaceCharacters).sub(' ', text)

