#!/usr/bin/python
# -*- coding: utf-8 -*
from DomElementMethods import *

obj = Element("AAA")
obj.text = "pouet"
print obj.text
obj.tail = "test"
print tostring(obj)
