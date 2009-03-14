#!/usr/bin/python
# -*- coding: utf-8 -*

from xml.dom.minidom import *
from xml.dom import InvalidAccessErr

ATTR_BLOCK="block"

def getAttributes(self):
	"""
		Returns a sorted array containing the element's attributes and their values but the 'block' attribute.
		This provides a convenient way to test the equality beween two elements' attributes and values :
		(e1.getAttributes() == e2.getAttributes) <=> Excluding the 'block' attribute, e1 and e2 have same attributes with same values.
	"""
	attrs=[]
	if self.hasAttributes():
		children=self.attributes
		for i in range(children.length):
			if children.item(i).name != ATTR_BLOCK:
				attrs.append([children.item(i).name, self.getAttribute(children.item(i).name)])
	attrs.sort()
	return attrs

def getBlocking(self):
	"""
		A more convenient way to access the 'block' special attribute.
	"""
	if (not self.hasAttribute(ATTR_BLOCK)):
		return False
	else:
		return bool(self.getAttribute(ATTR_BLOCK))

def setBlocking(self,blocking):
	"""
		Sets the 'block' special attribute.
	"""
	self.__oldSetAttribute(ATTR_BLOCK,blocking)

def getText(self):
	"""
		Returns the first (should be the only one) Text node's data
	"""
	if self.hasChildNodes():
		children=self.childNodes
		for i in range(children.length):
			if children.item(i).nodeType == Node.TEXT_NODE:
				return children.item(i).data
	return None

def setText(self,text):
	"""
		Deletes every CDATASection or Text child and appends a new CDATASection containing the text.
		Every Element child will be deleted by appendChild()
	"""
	self.delText()
	textNode = Text()
	textNode.data = text
	self.appendChild(textNode)

def appendText(self,text):
	"""
		Appends a new Text containing the text
		Every Element child will be deleted by appendChild()
	"""
	self.delText()
	textNode = Text()
	textNode.data = text
	self.appendChild(textNode)

def delText(self):
	"""
		Removes any Text child
	"""
	if self.hasChildNodes():
		children=self.childNodes
		for i in range(children.length):
			if children.item(i).nodeType == Node.TEXT_NODE:
				self.removeChild(children.item(i))

def delElements(self):
	"""
		Removes any Text or CDATASection child
	"""
	if self.hasChildNodes():
		children=self.childNodes
		for i in range(children.length):
			if children.item(i).nodeType == Node.ELEMENT_NODE:
				self.removeChild(children.item(i))

def checkUnicity(self, elt):
	"""
		Checks if no child element has the same name and the same attributes,
	"""
	if self.hasChildNodes():
		children=self.childNodes
		for i in range(children.length):
			if children.item(i).nodeType == Node.ELEMENT_NODE and children.item(i).tagName == elt.tagName and children.item(i).getAttributes() == elt.getAttributes():
				return False
	return True

def appendChild(self, newChild):
	"""
		Works as the standard function, but :
		- If newChild is an Element, checks unicity before adding, and deletes every Text or CDATASection
		- If newChild is a Text , deletes every Element child, adds it and the normalize().
	"""
	if newChild.nodeType == Node.ELEMENT_NODE:
		if (not self.__checkUnicity(newChild)):raise InvalidAccessErr
		self.delText()
		self.__oldAppendChild(newChild)
	elif newChild.nodeType == Node.TEXT_NODE or newChild.nodeType == Node.CDATA_SECTION_NODE:
		self.delElements()
		self.__oldAppendChild(newChild)
		self.normalize()
	else:
		self.__oldAppendChild(newChild)

def insertBefore(self, newChild, refChild):
	"""
		Works as the standard function, but :
		- If newChild is an Element, checks unicity before adding, and deletes every Text or CDATASection
		- If newChild is a Text , deletes every Element child, adds it and the normalize().
	"""
	if newChild.nodeType == Node.ELEMENT_NODE:
		if (not self.__checkUnicity(newChild)):raise InvalidAccessErr
		self.delText()
		self.__oldInsertBefore(newChild, refChild)
	elif newChild.nodeType == Node.TEXT_NODE or newChild.nodeType == Node.CDATA_SECTION_NODE:
		self.delElements()
		self.__oldInsertBefore(newChild, refChild)
		self.normalize()
	else:
		self.__oldInsertBefore(newChild, refChild)

def setAttribute(self, name, value):

	#Computation of new attribute list
	newattrs=self.getAttributes()
	if not self.hasAttribute(name):
		#if attribute doesn't exist yet, just add it
		newattrs.append([name, value])
		newattrs.sort()
	else: # replace it !
		for i, attr in enumerate(newattrs):
			if attr[1] == name:
				newattrs[i] = [name, value]
				break
	
	#check if no brother element has the future attribute set	
	parent = self.parentNode
	if parent != None and parent.nodeType == Node.ELEMENT_NODE:
		brothers = parent.childNodes
		for i in range(brothers.length):
			br=brothers.item(i)
			if br.nodeType == Node.ELEMENT_NODE and not br.isSameNode(self) and br.tagName == self.tagName and br.getAttributes() == newattrs:
				raise InvalidAccessErr
	self.__oldSetAttribute(name, value)
