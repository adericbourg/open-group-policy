#!/usr/bin/python
# -*- coding: utf-8 -*

from lxml.etree import *
from ElementMethods import *

OGP_PARSER = XMLParser()
OGP_PARSER.set_element_class_lookup(ElementDefaultClassLookup(element=OgpElement))
Element = OGP_PARSER.makeelement
