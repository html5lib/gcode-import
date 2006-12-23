"""HTML parser based on the WHATWG Web Applications 1.0
specifcation. This module is designed to parse real-world HTML
documents into trees with errorhandling modelled on popular web
browsers. This makes the library very robust against invalid
documents.

  HTMLParser - the main parser class

Usage:
#Basic import and parse import html5lib
f = open("mydocument.html")
parser = html5lib.HTMLParser()
doc = parser.parse(f)

The return value is a very, very simplistic DOM tree, comprised of Node 
objects.
"""
from parser import HTMLParser 
