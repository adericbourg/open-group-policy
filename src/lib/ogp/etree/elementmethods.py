#!/usr/bin/python
# -*- coding: utf-8 -*

from lxml.etree import *
from copy import deepcopy

ATTR_BLOCK = "block"
ATTR_ID = "id"

class OgpElement(ElementBase):
	
	def __setattr__(self, item, value):
		if item == "text" and value is not None:
			#print "Deleting all subelements..."
			#print "self.tag: " + self.tag + " text: " + value
			self.delElements()
		if item == "tail":
			#print "Tail must be none"
			value = None
		
		ElementBase.__setattr__(self, item, value)

	def __getAttributes(self):
		res = dict()
		for key in self.attrib:
			if key != ATTR_BLOCK:
				res[key] = self.attrib[key]
		return res
	attributes = property(__getAttributes)

	def __getBlocking(self):
		"""
			A more convenient way to access the 'block' special attribute.
		"""
		b = self.get(ATTR_BLOCK)
		if b is None:
			return False
		else:
			return bool(b)

	def __setBlocking(self, blocking):
		"""
			Sets the 'block' special attribute.
		"""
		assert isinstance(blocking, bool)
		if blocking:
			self.attrib[ATTR_BLOCK] = str(blocking).lower()
		else:
			try:
				del self.attrib[ATTR_BLOCK]
			except:
				pass
	blocking = property(__getBlocking, __setBlocking)

	def delElements(self):
		"""
			Removes any Text or CDATASection child
		"""
		for e in self:
			self.remove(e)

	def __checkUnicity(self, elt):
		"""
			Checks if no child element has the same name and the same attributes,
		"""
		assert isinstance(elt, OgpElement)
		for e in self:
			if e.tag == elt.tag and e.attributes == elt.attributes:
				return False
		return True

	def append(self, newChild):
		"""
			Works as the standard function, but :
			- If newChild is an Element, checks unicity before adding, and deletes every Text or CDATASection
			- If newChild is a Text , deletes every Element child, adds it and the normalize().
		"""
		assert isinstance(newChild, OgpElement)
		if (not self.__checkUnicity(newChild)):raise OgpXmlError('append: element is not unique')
		self.text = None
		ElementBase.append(self, newChild)

	def insert(self, index, newChild):
		"""
			Works as the standard function, but :
			- If newChild is an Element, checks unicity before adding, and deletes every Text or CDATASection
			- If newChild is a Text , deletes every Element child, adds it and the normalize().
		"""
		assert isinstance(newChild, OgpElement)
		assert isinstance(index, int)

		if (not self.__checkUnicity(newChild)):raise OgpXmlError('insert: element is not unique')
		self.text = None
		ElementBase.insert(self, index, element)

	def extend(self, elements):
		for element in elements:
			assert isinstance(element, OgpElement)
			if (not self.__checkUnicity(element)):raise OgpXmlError('extend: element is not unique')
			ElementBase.append(self, element) 

	def set(self, name, value):
		assert isinstance(name, str)
		assert isinstance(value, str)
		#Computation of new attribute list
		newattrs=self.attributes
		newattrs[name] = value
		
		#check if no brother element has the future attribute set	
		parent = self.getparent()
		if parent is not None:
			for br in parent:
				if br is not self and br.tag == self.tag and br.attributes == newattrs:
					raise OgpXmlError('set: element would no more be unique')
		self.attrib[name] = value

	def merge(self, peer):
		"""
			Merges self with peer. peer is considered as the "child" conf (LDAP speaking), so that it has precendence on self.
			See plugin documentation for further details on the algorithm
		"""
		assert isinstance(peer, OgpElement)

		#if self and peer are not exactly the same (i.e. same name and same attributes),
		#raise OgpXmlError.
		if self.tag != peer.tag or self.attributes != peer.attributes:
			raise OgpXmlError('merge: peer has not same name or attributes')
		
		#Nodes must have same content. If not, raise OgpXmlError
		if not ((self.text is None) ^ (peer.text is not None)):
			raise OgpXmlError('merge: peer has not same type of content')

		#if blocking, stop here
		if self.blocking:return

		#First case : nodes contains Text
		if self.text is not None:
			self.text = peer.text
			return
		else: #Second Case : nodes contains nodes
			self.__reorder_ids(peer)
			
			selfCommon=dict()

			peerNotCommon=[]
			peerCommon=dict()

			for selfE in self:
				for peerE in peer:
					if selfE.tag == peerE.tag and selfE.attributes == peerE.attributes:
						selfCommon[(selfE.tag, str(selfE.attributes))] = selfE

			for peerE in peer:
				common = False
				for selfE in self:
					if peerE.tag == selfE.tag and peerE.attributes == selfE.attributes:
						peerCommon[(peerE.tag, str(peerE.attributes))] = peerE
						common = True
				if not common:
						peerNotCommon.append(peerE)
			
			#add peer children wich are not in common
			for e in peerNotCommon:
				self.append(deepcopy(e))

			#merge common children
			for k, e in selfCommon.iteritems():
				e.merge(deepcopy(peerCommon[k]))

	def __reorder_ids(self, peer):
		assert isinstance(peer, OgpElement)

		peerMaxId = 0
		if len(peer) > 0 and len(self) > 0:
			for e in peer:
				id = e.get(ATTR_ID)
				if id is not None and int(id) > peerMaxId:
					peerMaxId = int(id)

			for e in self:
				id = e.get(ATTR_ID)
				if id is not None:
					e.set(ATTR_ID, str(int(id) + peerMaxId + 1))

	def toString(self, xsl=None, params=None):
		if xsl is None:
			return tostring(self)
		else:
			self.__processXsl(xsl, params)

	def __processXsl(self, xsl, params):
		transform = XSLT(xsl)
		if params is None:
			return str(transform(self))
		else:
			return str(transform(self), params)

class OgpXmlError(Exception):
	def __init__(self, value):
		assert isinstance(value, str)
		self.value = value
	
	def __str__(self):
					return repr("OgpXmlError: " + self.value)

class OgpElementClassLookup(PythonElementClassLookup):
	def lookup(self, document, element):
		return OgpElement # defined elsewhere

