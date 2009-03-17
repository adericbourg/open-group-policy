#!/usr/bin/python
# -*- coding: utf-8 -*
from lxml.etree import *
from DomElementMethods import *
import StringIO

parent=fromstring('<ogp><a>parent</a><b block="True">parent</b><c><parent/></c></ogp>', OGP_PARSER)
child=fromstring('<ogp><a>child</a><b>child</b><c><child/></c></ogp>', OGP_PARSER)

print "parent :\n" + parent.toString()
print "child :\n" + child.toString()
parent.merge(child)
print "merge :\n" + parent.toString()
