import html5lib
from html5lib import serializer, treewalkers, treebuilders
from xml.sax.saxutils import escape

"""
    A lot of this code is copied from the deprecated html5lib sanitizer
    https://github.com/html5lib/html5lib-python/blob/master/html5lib/filters/sanitizer.py
"""

ELEMENTS_NOT_ALLOWED = ["script", "svg", "math", "style", "body", "head", "iframe", "embed"]

def sanitize_token(token):
        token_type = token["type"]
        if token_type in ("StartTag", "EndTag", "EmptyTag"):
            name = token["name"]
            namespace = token["namespace"]
            print(f"{namespace}: {name}")
            if namespace != "http://www.w3.org/1999/xhtml":
                return disallowed_token(token)
            if name in ELEMENTS_NOT_ALLOWED:
                return disallowed_token(token)
            return allowed_token(token)
        elif token_type == "Comment":
            pass
        else:
            return token

def allowed_token(token):
    if "data" in token:
        attrs = token["data"]
        attr_names = set(attrs.keys())
        print(attr_names)
        for to_remove in [n for n in attr_names if n[1].startswith("on")]:
            del token["data"][to_remove]
            attr_names.remove(to_remove)
    return token

def disallowed_token(token):
        token_type = token["type"]
        if token_type == "EndTag":
            token["data"] = f"</{token['name']}>"
        elif token["data"]:
            assert token_type in ("StartTag", "EmptyTag")
            attrs = []
            for (ns, name), v in token["data"].items():
                attrs.append(' %s="%s"' % (name if ns is None else "%s:%s" % ("prefixes[ns]", name), escape(v)))
            token["data"] = "<%s%s>" % (token["name"], ''.join(attrs))
        else:
            token["data"] = f"<{token['name']}>"
        if token.get("selfClosing"):
            token["data"] = token["data"][:-1] + "/>"

        token["type"] = "Characters"

        del token["name"]
        return token

def sanitize(stream):    
    for token in iter(stream):
        token = sanitize_token(token)
        if token:
            yield token

def sanitize_html(value):
    p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
    dom_tree = p.parseFragment(value)
    walker = treewalkers.getTreeWalker("dom")
    stream = walker(dom_tree)
    clean_stream = sanitize(stream)

    s = serializer.HTMLSerializer(omit_optional_tags=False)
    return "".join(s.serialize(clean_stream))
