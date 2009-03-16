#!/usr/bin/python
# -*- coding: utf-8 -*

from xml.dom.minidom import *
from xml.dom import InvalidAccessErr

ATTR_BLOCK="block"
ATTR_ID="id"

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
	if parent is not None and parent.nodeType == Node.ELEMENT_NODE:
		brothers = parent.childNodes
		for i in range(brothers.length):
			br=brothers.item(i)
			if br.nodeType == Node.ELEMENT_NODE and not br.isSameNode(self) and br.tagName == self.tagName and br.getAttributes() == newattrs:
				raise InvalidAccessErr
	self.__oldSetAttribute(name, value)

def merge(self, peer):
	"""
		Merges self with peer. peer is considered as the "child" conf (LDAP speaking), so that it has precendence on self.
		See plugin documentation for further details on the algorithm
	"""
	#if self and peer are not exactly the same (i.e. same name and same attributes),
	#raise InvalidAccessErr.
	if self.tagName != peer.tagName or self.getAttributes() != peer.getAttributes():
		raise InvalidAccessErr
	
	#Nodes must have same content. If not, raise InvalidAccessErr
	if (self.getText() is None and peer.getText() is not None) or (self.getText() is not None and peer.getText() is None):
		raise InvalidAccessErr

	#First case : nodes contains Text
	if self.getText() is not None:
		self.setText(peer.getText())
		return
	else: #Second Case : nodes contains nodes
		self.reorder_ids(peer)
		
		selfCommon=dict()

		peerNotCommon=[]
		peerCommon=dict()

		for i in range(self.childNodes.length):
			selfE = self.childNodes.item(i)
			for j in range(peer.childNodes.length):
				peerE = peer.childNodes.item(j)
				if selfE.tagName == peerE.tagName and selfE.getAttributes() == peerE.getAttributes():
					selfCommon[[selfE.tagName, selfE.getAttributes()]] = selfE

		for i in range(peer.childNodes.length):
			peerE = peer.childNodes.item(i)
			common = False
			for j in range(self.childNodes.length):
				selfE = self.childNodes.item(j)
				if peerE.tagName == selfE.tagName and peerE.getAttributes() == selfE.getAttributes():
					peerCommon[[peerE.tagName, peerE.getAttributes()]] = peerE
					common = True
			if not common:
					peerNotCommon.append(peerE)
		
		#add peer children wich are not in common
		for e in peerNotCommon:
			self.appendChild(e.clone(deep))

		#merge common children
		for k, e in selfCommon.iteritems():
			e.merge(peerCommon[k].clone(deep))


def reorder_ids(self, peer):
	peerMaxId = 0
	if peer.hasChildNodes() and self.hasChildNodes:
		for i in range(peer.childNodes.length):
			e=peer.childNodes.item(i)
			if e.nodeType == Node.ELEMENT_NODE and e.hasAttribute(ATTR_ID) and int(e.getAttribute(ATTR_ID)) > peerMaxId:
				peerMaxId = int(e.getAttribute(ATTR_ID))

		for i in range(self.childNodes.length):
			e=self.childNodes.item(i)
			if e.nodeType == Node.ELEMENT_NODE and e.hasAttribute(ATTR_ID):
				e.setAttribute(ATTR_ID, str(int(e.getAttribute(ATTR_ID)) + peerMaxId + 1))

