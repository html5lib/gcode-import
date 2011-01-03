import _base

class Filter(_base.Filter):
    def __init__(self, source, encoding):
        _base.Filter.__init__(self, source)
        self.encoding = encoding

    def __iter__(self):
        state = "pre_head"
        meta_found = (self.encoding is None)
        pending = []

        for token in _base.Filter.__iter__(self):
            type = token["type"]
            if type == "StartTag":
                if token["name"].lower() == "head":
                    state = "in_head"

            elif type == "EmptyTag":
                if token["name"].lower() == "meta":
                   # replace charset with actual encoding
                   has_http_equiv_content_type = False
                   content_index = -1
                   for i,attr in enumerate(token["data"]):
                       namespace = attr["namespace"]
                       name = attr["name"]
                       value = attr["value"]
                       if namespace != None:
                           continue
                       elif name.lower() == 'charset':
                          token["data"][i]["value"] = self.encoding
                          meta_found = True
                          break
                       elif name == 'http-equiv' and value.lower() == 'content-type':
                           has_http_equiv_content_type = True
                       elif name == 'content':
                           content_index = i
                   else:
                       if has_http_equiv_content_type and content_index >= 0:
                           token["data"][content_index]["value"] = u'text/html; charset=%s' % self.encoding
                           meta_found = True

                elif token["name"].lower() == "head" and not meta_found:
                    # insert meta into empty head
                    yield {"type": "StartTag", "name": "head",
                           "data": token["data"]}
                    yield {"type": "EmptyTag", "name": "meta",
                           "data": [{"namespace": None, "name": "charset", "value": self.encoding}]}
                    yield {"type": "EndTag", "name": "head"}
                    meta_found = True
                    continue

            elif type == "EndTag":
                if token["name"].lower() == "head" and pending:
                    # insert meta into head (if necessary) and flush pending queue
                    yield pending.pop(0)
                    if not meta_found:
                        yield {"type": "EmptyTag", "name": "meta",
                               "data": [{"namespace": None, "name": "charset", "value": self.encoding}]}
                    while pending:
                        yield pending.pop(0)
                    meta_found = True
                    state = "post_head"

            if state == "in_head":
                pending.append(token)
            else:
                yield token
