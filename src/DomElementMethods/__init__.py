#!/usr/bin/python
# -*- coding: utf-8 -*
from xml.dom.minidom import * 
from ElementMethods import *

Element.getAttributes=getAttributes

Element.getBlocking=getBlocking
Element.setBlocking=setBlocking

Element.setText=setText
Element.getText=getText
