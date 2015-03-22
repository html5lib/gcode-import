# Using html5lib #

## Installation ##

Releases can be installed using `pip` in the usual way:
```
 $ pip install html5lib
```

The development version can be installed by cloning the source repository using mercurial and running:
```
 $ python setup.py develop
```
in the `python` directory.

## Tests ##

The development version of html5lib comes with an extensive testsuite. All the tests can be run by invoking
runtests.py in the tests/ directory or by running
```
$ python setup.py nosetests
```

## Parsing HTML ##

Simple usage follows this pattern:
```
import html5lib
f = open("mydocument.html")
doc = html5lib.parse(f)
```
This will return a tree in a custom "simpletree" format. More interesting is the ability to use a variety of standard tree formats; currently minidom, ElementTree, lxml and BeafutifulSoup (deprecated) formats are supported by default. To do this you pass a string indicating the name of the tree format to use as the "treebuilder" argument to the parse method:
```
import html5lib
f = open("mydocument.html")
doc = html5lib.parse(f, treebuilder="lxml")
```

It is also possible to explicitly create a parser object:
```
import html5lib
f = open("mydocument.html")
parser = html5lib.HTMLParser()
doc = parser.parse(f)
```
To output non-simpletree tree formats when explicitly creating a parser, you need to pass a TreeBuilder class as the "tree" argument to the HTMLParser. For
the built-in treebuilders this can be conveniently obtained from the treebuilders.getTreeBuilder function e.g. for minidom:
```
import html5lib
from html5lib import treebuilders

f = open("mydocument.html")
parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))
minidom_document = parser.parse(f)
```

For a BeautifulSoup tree replace the string "dom" with "beautifulsoup". For
ElementTree the procedure is slightly more involved as there are many libraries
that support the ElementTree API. Therefore getTreeBuilder accepts a second
argument which is the ElementTree implementation that is desired (in the future
this may be extended, for example to allow multiple DOM libraries to be used):

```
import html5lib
from html5lib import treebuilders
from xml.etree import cElementTree

f = open("mydocument.html")
parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("etree", cElementTree))
etree_document = parser.parse(f)
```

If you are using the excellent lxml library, using the generic etree treebuilder described above with fail. Instead you must use the lxml builder:

```
import html5lib
from html5lib import treebuilders
from lxml import etree

f = open("mydocument.html")
parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("lxml"))
etree_document = parser.parse(f)
```

### SAX Events ###
The WHATWG spec is not very streaming-friendly as it requires rearrangement of
subtrees in some situations. However html5lib allows SAX events to be created
from a DOM tree using html5lib.treebuilders.dom.dom2sax

### Character encoding ###

Parsed trees are always Unicode. However a large variety of input encodings are supported. The encoding of the document is determined in the following way:

  * The encoding may be explicitly specified by passing the name of the encoding as the encoding parameter to HTMLParser.parse

  * If no encoding is specified, the parser will attempt to detect the encoding from a 

&lt;meta&gt;

 element in the first 512 bytes of the document (this is only a partial implementation of the current HTML 5 specification)

  * If no encoding can be found and the chardet library is available, an attempt will be made to sniff the encoding from the byte pattern

  * If all else fails, the default encoding (usually Windows-1252) will be used

#### Examples ####

Explicit encoding specification:
```
import html5lib
import urllib2
p = html5lib.HTMLParser()
p.parse(urllib2.urlopen("http://yahoo.co.jp", encoding="euc-jp").read())
```

Automatic detection from a meta element:
```
import html5lib
import urllib2
p = html5lib.HTMLParser()
p.parse(urllib2.urlopen("http://www.mozilla-japan.org/").read())
```

## Sanitizing Tokenizer ##

When building web applications it is often necessary to remove unsafe markup and
CSS from user entered content. html5lib provides a custom tokenizer for this
purpose. It only allows known safe element tokens through and converts others
to text. Similarly, a variety of unsafe CSS constructs are removed from the
stream. For more details on the default configuration of the sanitizer, see
http://wiki.whatwg.org/wiki/Sanitization_rules The sanitizer can be used by
passing it as the tokenizer argument to the parser:
```
import html5lib
from html5lib import sanitizer

p = html5lib.HTMLParser(tokenizer=sanitizer.HTMLSanitizer)
p.parse("<script>alert('foo');</script>")
```

## Treewalkers ##

Treewalkers provide a streaming view of a tree. They are useful for filtering
and serializing the stream. html5lib provides a variety of treewalkers for
working with different tree types. For example, to stream a dom tree:
```
from html5lib import treewalkers
walker = treewalkers.getTreeWalker("dom")

stream = walker(dom_tree) #stream is an iterable representing each token in the
                          #tree
```

Treewalkers are avaliable for all the tree types supported by the HTMLParser plus
xml.dom.pulldom ("pulldom"), genshi streams ("genshi") and a lxml-optimized
elementtree ("lxml"). As for the treebulders, treewalkers.getTreeWalker takes a
second argument implementation containing a object implementing the ElementTree
API.

### Sanitization using treewalkers ###
You may wish to sanitize content from an which has been parsed into a tree by some other code. This may be done using the sanitizer filter:

```
from html5lib import treewalkers, filters
from html5lib.filters import sanitizer

walker = treewalkers.getTreeWalker("dom")

stream = walker(dom_tree)
clean_stream = sanitizer.Filter(stream)
```

### Serialization of Streams ###

html5lib provides HTML and XHML serializers which work on streams produced by the treewalkers. These are implemented as generators with each item in the generator representing a single tag. A full example of parsing and serializing content looks like:

```
import html5lib
from html5lib import treebuilders, treewalkers, serializer
from html5lib.filters import sanitizer

p = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("dom"))

dom_tree = p.parse("<p><strong>Hello</strong> World</p>")

walker = treewalkers.getTreeWalker("dom")

stream = walker(dom_tree)

s = serializer.htmlserializer.HTMLSerializer(omit_optional_tags=False)
output_generator = s.serialize(stream)

for item in output_generator:
    print item

<html>
<head>
</head>
<body>
<p>
<strong>
Hello
</strong>
 
World
</p>
</body>
</html>

```


# Bugs #

Please report any bugs on the issue tracker:
http://code.google.com/p/html5lib/issues/list

# Ports #

There is a listing of [html5lib ports](Ports.md) to JavaScript, Ruby and more.

# Get Involved #

Contributions to code or documenation are actively encouraged. Submit
patches to the issue tracker or discuss changes on irc in the #whatwg
channel on freenode.net