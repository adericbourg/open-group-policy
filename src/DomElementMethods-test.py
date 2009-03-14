#!/usr/bin/python
# -*- coding: utf-8 -*
from xml.dom.minidom import *
import DomElementMethods

obj = Element("test")
a = Element("a")
obj.appendChild(a)
b = Element("b")
obj.appendChild(b)
a2 = Element("a")
a.setAttribute("a","a")
obj.appendChild(a2)
a2.setAttribute("a","a")
