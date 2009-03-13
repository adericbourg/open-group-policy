#!/usr/bin/python
# -*- coding: utf-8 -*

from xml.dom.minidom import *
ATTR_BLOCK="block"

def getAttributes(self):
	pass

def getBlocking(self):
	"""
		A more convenient way to access
	"""
	print "get"
	if (not self.hasAttribute(ATTR_BLOCK)):
		return False
	else:
		return bool(self.getAttribute(ATTR_BLOCK))

def setBlocking(self,blocking):
	print "set"
	self.setAttribute(ATTR_BLOCK,blocking)

def getText(self):
	return self.__text

def setText(self,text):
	self.__text=text
