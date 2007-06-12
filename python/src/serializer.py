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
        openElements = []
        in_cdata = False
        self.errors = []
        if encoding and self.inject_meta_charset:
            #treewalker = self.filter_inject_meta_charset(treewalker, encoding)
            raise NotImplementedError
        # XXX: WhitespaceFilter should be used before OptionalTagFilter
        # for maximum efficiently of this latter filter
        if self.strip_whitespace:
            treewalker = WhitespaceFilter(treewalker)

        while True:
            if self.tree.type in ("Document", "DocumentFragment"):
                if self.tree.hasChildren:
                    self.tree.firstChild()
                    continue

            elif self.tree.type == "Doctype":
                assert not openElements
                doctype = u"<!DOCTYPE %s>" % self.tree.name
                if encoding:
                    yield doctype.encode(encoding)
                else:
                    yield doctype

            elif self.tree.type == "Element":
                yield self.startTag(encoding)
                if self.tree.name not in voidElements:
                    openElements.append(self.tree.name)
                    if self.tree.hasChildren:
                        self.tree.firstChild()
                        continue
                else:
                    if self.tree.hasChildren:
                        pass # error

            elif self.tree.type == "Text":
                text = self.tree.value
                if in_cdata and text.find("</") >= 0:
                    self.serializeError(_("Unexpected </ in CDATA"))
                if encoding:
                    yield escape_text(text, encoding)
                else:
                    yield text \
                        .replace("&", "&amp;") \
                        .replace("<", "&lt;")  \
                        .replace(">", "&gt;")

            elif self.tree.type == "Comment":
                yield "%s<!--%s-->" % ('  '*len(openElements), self.tree.value)

            while self.tree.type not in ("Document", "DocumentFragment"):
                if self.tree.type == "Element":
                  if self.tree.name not in voidElements:
                    assert self.tree.name == openElements.pop()
                    yield "%s</%s>" % ('  '*len(openElements), self.tree.name)

                if self.tree.nextSibling():
                    break
                self.tree.parentNode()
            else:
                raise StopIteration

    def _startTag(self, encoding):
        name = self.tree.name
        if name in self.cdata_elements:
            in_cdata = True
        elif in_cdata:
            self.serializeError(_("Unexpected child element of a CDATA element"))
        attrs = list(self.tree.attributes)
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
            yield "<%s%s>" % (name.encode(encoding, "strict"), "".join(attributes))
        else:
            yield u"<%s%s>" % (name, u"".join(attributes))

    def _endTag(self, encoding):
        name = self.tree.name
        if name in self.cdata_elements:
            in_cdata = False
        elif in_cdata:
            self.serializeError(_("Unexpected child element of a CDATA element"))
        end_tag = u"</%s>" % name
        if encoding:
            end_tag = end_tag.encode(encoding, "strict")
        yield end_tag

    def _comment(self, encoding):
        data = self.tree.value
        if data.find("--") >= 0:
            self.serializeError(_("Comment contains --"))
        comment = u"<!--%s-->" % token["data"]
        if encoding:
            comment = comment.encode(encoding, unicode_encode_errors)
        yield comment


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
