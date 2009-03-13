#!/usr/bin/python
# -*- coding: utf-8 -*
from xml.dom.minidom import *
import DomElementMethods

obj = Element("test")
print obj.getBlocking()  # get
obj.setBlocking(True)    # set
print obj.getBlocking()  # get

