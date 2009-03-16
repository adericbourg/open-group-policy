#!/usr/bin/python
# -*- coding: utf-8 -*

from ElementMethods import *
from lxml.etree import *

OGP_PARSER = XMLParser()
OGP_PARSER.set_element_class_lookup(ElementDefaultClassLookup(element=OgpElement))
Element = OGP_PARSER.makeelement
