#!/usr/bin/python
# -*- coding: utf-8 -*
from xml.dom.minidom import * 
from ElementMethods import *

Element.getAttributes=getAttributes

Element.getBlocking=getBlocking
Element.setBlocking=setBlocking

Element.setText=setText
Element.getText=getText
Element.appendText=appendText
Element.delText=delText

Element.delElements=delElements

Element.__checkUnicity=checkUnicity

Element.__oldAppendChild=Element.appendChild
Element.appendChild=appendChild

Element.__oldInsertBefore=Element.insertBefore
Element.insertBefore=insertBefore

Element.__oldSetAttribute=Element.setAttribute
Element.setAttribute=setAttribute
