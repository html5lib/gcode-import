try:
    frozenset
except NameError:
    # Import from the sets module for python 2.3
    from sets import ImmutableSet as frozenset

import gettext
_ = gettext.gettext

from filters.whitespace import Filter as WhitespaceFilter
from filters.optionaltags import Filter as OptionalTagFilter

from constants import voidElements, booleanAttributes, spaceCharacters

spaceCharacters = u"".join(spaceCharacters)

try:
    from codecs import register_error, xmlcharrefreplace_errors
except ImportError:
    unicode_encode_errors = "strict"
else:
    unicode_encode_errors = "htmlentityreplace"

    from constants import entities

    encode_entity_map = {}
    for k, v in entities.items():
        if v != "&" and encode_entity_map.get(v) != k.lower():
            # prefer &lt; over &LT; and similarly for &amp;, &gt;, etc.
            encode_entity_map[v] = k

    def htmlentityreplace_errors(exc):
        if isinstance(exc, (UnicodeEncodeError, UnicodeTranslateError)):
            res = []
            for c in ex.object[exc.start:exc.end]:
                c = encode_entity_map.get(c)
                if c:
                    res.append("&")
                    res.append(c)
                    res.append(";")
                else:
                    res.append(c.encode(exc.encoding, "xmlcharrefreplace"))
            return (u"".join(res), exc.end)
        else:
            return xmlcharrefreplace_errors(exc)

    register_error(unicode_encode_errors, htmlentityreplace_errors)

    del register_error

def escape_text(text, encoding):
    return text.replace("&", "&amp;").encode(encoding, unicode_encode_errors)

_ROOT_MARKER = "<#ROOT#>"

class HTMLSerializer(object):
    cdata_elements = frozenset(("style", "script", "xmp", "iframe", "noembed", "noframes", "noscript"))

    quote_attr_values = False
    quote_char = '"'
    use_best_quote_char = True
    minimize_boolean_attributes = True

    use_trailing_solidus = False
    space_before_trailing_solidus = True

    omit_optional_tags = True

    strip_whitespace = False

    inject_meta_charset = True

    def __init__(self, **kwargs):
        if kwargs.has_key('quote_char'):
            self.use_best_quote_char = False
        for attr in ("quote_attr_values", "quote_char", "use_best_quote_char",
          "minimize_boolean_attributes", "use_trailing_solidus",
          "space_before_trailing_solidus", "omit_optional_tags",
          "strip_whitespace", "inject_meta_charset"):
            setattr(self, attr, kwargs.get(attr, getattr(self, attr)))
        self.errors = []
        self.strict = False

    def serialize(self, treewalker, encoding=None):
        openElements = [] # list of (name, in_cdata) tuples
        self.errors = []
        if encoding and self.inject_meta_charset:
            #treewalker = self.filter_inject_meta_charset(treewalker, encoding)
            raise NotImplementedError
        # XXX: WhitespaceFilter should be used before OptionalTagFilter
        # for maximum efficiently of this latter filter
        if self.strip_whitespace:
            treewalker = WhitespaceFilter(treewalker)

        while True:
            if treewalker.type in ("Document", "DocumentFragment"):
                openElements.append((_ROOT_MARKER, False))
                if treewalker.hasChildren:
                    treewalker.firstChild()
                    continue

            elif treewalker.type == "Doctype":
                assert len(openElements) == 1
                yield self._doctype(treewalker.name, encoding)

            elif treewalker.type == "Element":
                name = treewalker.name
                if openElements[-1][1]: # in_cdata
                    self.serializeError(_("Unexpected child element of a CDATA element"))
                yield self._startTag(name, treewalker.attributes, encoding)
                if name not in voidElements:
                    openElements.append((name, openElements[-1][1] or name in self.cdata_elements))
                    if treewalker.hasChildren:
                        treewalker.firstChild()
                        continue
                else:
                    if treewalker.hasChildren:
                        self.serializeError(_("Void element has children: %s") % name)

            elif treewalker.type == "Text":
                text = treewalker.value
                if openElements[-1][1] and text.find("</") >= 0: # in_cdata
                    self.serializeError(_("Unexpected </ in CDATA"))
                yield self._text(text, encoding)

            elif treewalker.type == "Comment":
                yield self._comment(treewalker.value, encoding)

            while openElements:
                parent = openElements.pop()
                if parent[0] is not _ROOT_MARKER and parent[0] not in voidElements:
                    yield self._endTag(parent[0], encoding)

                if treewalker.nextSibling():
                    break
                treewalker.parentNode()
            else:
                raise StopIteration

    def _doctype(self, name, encoding):
        doctype = u"<!DOCTYPE %s>" % name
        if encoding:
            doctype = doctype.encode(encoding)
        return doctype

    def _startTag(self, name, attrs, encoding):
        attrs = list(attrs)
        attrs.sort()
        attributes = []
        for k,v in attrs:
            if encoding:
                k = k.encode(encoding, "strict")
            attributes.append(' ')

            attributes.append(k)
            if not self.minimize_boolean_attributes or \
              (k not in booleanAttributes.get(name, tuple()) \
              and k not in booleanAttributes.get("", tuple())):
                attributes.append("=")
                if self.quote_attr_values or not v:
                    quote_attr = True
                else:
                    quote_attr = reduce(lambda x,y: x or (y in v),
                        spaceCharacters + "<>\"'", False)
                if encoding:
                    v = escape_text(v, encoding)
                else:
                    v = v.replace("&", "&amp;")
                if quote_attr:
                    quote_char = self.quote_char
                    if self.use_best_quote_char:
                        if "'" in v and '"' not in v:
                            quote_char = '"'
                        elif '"' in v and "'" not in v:
                            quote_char = "'"
                    if quote_char == "'":
                        v = v.replace("'", "&#39;")
                    else:
                        v = v.replace('"', "&quot;")
                    attributes.append(quote_char)
                    attributes.append(v)
                    attributes.append(quote_char)
                else:
                    attributes.append(v)
        if name in voidElements and self.use_trailing_solidus:
            if self.space_before_trailing_solidus:
                attributes.append(" /")
            else:
                attributes.append("/")
        if encoding:
            return "<%s%s>" % (name.encode(encoding, "strict"), "".join(attributes))
        else:
            return u"<%s%s>" % (name, u"".join(attributes))

    def _endTag(self, name, encoding):
        end_tag = u"</%s>" % name
        if encoding:
            end_tag = end_tag.encode(encoding, "strict")
        return end_tag

    def _comment(self, data, encoding):
        if data.find("--") >= 0:
            self.serializeError(_("Comment contains --"))
        comment = u"<!--%s-->" % token["data"]
        if encoding:
            comment = comment.encode(encoding, unicode_encode_errors)
        return comment

    def _text(self, text, encoding):
        if encoding:
            return escape_text(text, encoding)
        else:
            return text \
                .replace("&", "&amp;") \
                .replace("<", "&lt;")  \
                .replace(">", "&gt;")


    def render(self, treewalker, encoding=None):
        if encoding:
            return "".join(list(self.serialize(treewalker, encoding)))
        else:
            return u"".join(list(self.serialize(treewalker)))

    def serializeError(self, data="XXX ERROR MESSAGE NEEDED"):
        # XXX The idea is to make data mandatory.
        self.errors.append(data)
        if self.strict:
            raise SerializeError

    def filter_inject_meta_charset(self, treewalker, encoding):
        done = False
        for token in treewalker:
            if not done and token["type"] == "StartTag" \
              and token["name"].lower() == "head":
                yield {"type": "EmptyTag", "name": "meta", \
                    "data": {"charset": encoding}}
            yield token

def SerializeError(Exception):
    """Error in serialized tree"""
    pass
