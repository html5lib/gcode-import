u"""A collection of modules for iterating through different kinds of
tree, generating tokens identical to those produced by the tokenizer
module.

To create a tree walker for a new type of tree, you need to do
implement a tree walker object (called TreeWalker by convention) that
implements a 'serialize' method taking a tree as sole argument and
returning an iterator generating tokens.
"""

from __future__ import absolute_import
from importlib import import_module

treeWalkerCache = {}

def getTreeWalker(treeType, implementation=None, **kwargs):
    u"""Get a TreeWalker class for various types of tree with built-in support

    treeType - the name of the tree type required (case-insensitive). Supported
               values are "simpletree", "dom", "etree" and "beautifulsoup"

               "simpletree" - a built-in DOM-ish tree type with support for some
                              more pythonic idioms.
                "dom" - The xml.dom.minidom DOM implementation
                "pulldom" - The xml.dom.pulldom event stream
                "etree" - A generic walker for tree implementations exposing an
                          elementtree-like interface (known to work with
                          ElementTree, cElementTree and lxml.etree).
                "lxml" - Optimized walker for lxml.etree
                "beautifulsoup" - Beautiful soup (if installed)
                "genshi" - a Genshi stream

    implementation - (Currently applies to the "etree" tree type only). A module
                      implementing the tree type e.g. xml.etree.ElementTree or
                      cElementTree."""

    treeType = treeType.lower()
    if treeType not in treeWalkerCache:
        if treeType in (u"dom", u"pulldom", u"simpletree"):
            mod = import_module(u"."+treeType, u"html5lib.treewalkers")
            treeWalkerCache[treeType] = mod.TreeWalker
        elif treeType == u"genshi":
            from . import genshistream
            treeWalkerCache[treeType] = genshistream.TreeWalker
        elif treeType == u"beautifulsoup":
            from . import soup
            treeWalkerCache[treeType] = soup.TreeWalker
        elif treeType == u"lxml":
            from . import lxmletree
            treeWalkerCache[treeType] = lxmletree.TreeWalker
        elif treeType == u"etree":
            from . import etree
            # XXX: NEVER cache here, caching is done in the etree submodule
            return etree.getETreeModule(implementation, **kwargs).TreeWalker
    return treeWalkerCache.get(treeType)
getTreeWalker.func_annotations = {}
