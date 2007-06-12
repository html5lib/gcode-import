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
    name = property(_getName, doc=_base.Filter.name)

    def _getValue(self):
        text = self.source.value
        if self.type == "Text":
            if self.collapsed_text:
                text = text.strip(spaceCharacters)
            text = collapse_spaces(text)
        return text
    value = property(_getValue, doc=_base.Filter.value)

    def firstChild(self):
        if preserve:
            preserve += 1
        self.source.firstChild(self)

    def parentNode(self):
        if preserve:
            preserve -= 1
        self.source.parentNode(self)

def collapse_spaces(text):
    return re.compile(u"[%s]+" % spaceCharacters).sub(' ', text)

