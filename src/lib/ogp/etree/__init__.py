#!/usr/bin/python
# -*- coding: utf-8 -*

from lxml.etree import *
from elementmethods  import *
from ogpxmlconsts import *

def parse(source, parser=None):
	if not hasattr(source, "read"):
		source = open(source, "rb")
	xml = ''
	for l in source.readlines():
		xml = xml + l
	source.close()
	if parser is None:
		return fromstring(xml)
	else:
		return fromstring(xml, parser)

OGP_PARSER = XMLParser()
OGP_PARSER.set_element_class_lookup(ElementDefaultClassLookup(element=OgpElement))
Element = OGP_PARSER.makeelement
