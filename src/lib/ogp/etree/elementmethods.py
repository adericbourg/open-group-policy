#!/usr/bin/python
# -*- coding: utf-8 -*

from lxml.etree import *
from copy import deepcopy
from ogpxmlconsts import *
from ogp.misc import *
import logging

def Element(name):
	logging.debug('Element(name=' + repr(name) + ')')
	OGP_PARSER = XMLParser()
	OGP_PARSER.set_element_class_lookup(ElementDefaultClassLookup(element=OgpElement))
	return OGP_PARSER.makeelement(name)

class OgpElement(ElementBase):
	"""
		lxml Element class providing redefined secure methods, compliant with the merge algorithm :
		delElements(self):
		append(self, newChild):
		insert(self, index, newChild):
		extend(self, elements):
		set(self, name, value):
		merge(self, peer):
		toString(self, xsl=None, params=None):
		attributes = property(__getAttributes)
		text attribute is protected : setting it to something not None deletes all subelements.
		tail is protected : if you try to modify it, it will still be None
		attrib if protected : you can only get a copy, so yon can't modify it without using self.set(name, value)
		
		You should NOT use other methods because it may crash the merge algorithm.
	"""

	def __setattr__(self, item, value):
		"""
			If target attribute is text, deletes all subelements.
			If targeted attribue is tail, forces value to None
		"""
		logging.debug('OgpElement.__setattr__(item=' + repr(item) + ', value=' + repr(value) + ')')
		if item == "text" and value is not None:
			self.delElements()
		if item == "tail":
			raise OgpXmlError('__setattr__: setting tail is forbiden, it must be None.')
		if item == "attrib":
			raise OgpXmlError('__setattr__: setting attributes directly is forbiden, please use self.set(name, value).')
		ElementBase.__setattr__(self, item, value)

	def __getattribute__(self, item):
		"""
			Protects the 'attrib' attributes by returning a copy instead of the real object.
			This returns a dict instance, not an _Attrib, but it seems to work
		"""
		logging.debug('OgpElement.__getattr__(item=' + repr(item) + ')')
		if item == "attrib":
			return dict(ElementBase.__getattribute__(self, item))
		else:
			return ElementBase.__getattribute__(self, item)

	def __getRealAttrib(self):
		"""
			Provides a private property to access the real 'attrib' attribute.
		"""
		logging.debug('OgpElement.__getRealAttrib()')
		return ElementBase.__getattribute__(self, "attrib")
	__attrib = property(__getRealAttrib)

	def __getAttributes(self):
		"""
			Returns the attributes dict(), without the OgpXmlConsts.ATTR_BLOCK ('block') attribute.
		"""
		logging.debug('OgpElement.__getAttributes()')
		res = dict()
		for key in self.attrib:
			if key != OgpXmlConsts.ATTR_BLOCK:
				res[key] = self.attrib[key]
		return res
	attributes = property(__getAttributes)

	def __getBlocking(self):
		"""
			A more convenient way to access the OgpXmlConsts.ATTR_BLOCK ('block') special attribute.
		"""
		logging.debug('OgpElement.__getBlocking()')
		b = self.get(OgpXmlConsts.ATTR_BLOCK)
		if b is None:
			return False
		else:
			return smart_bool(b)

	def __setBlocking(self, blocking):
		"""
			Sets the OgpXmlConsts.ATTR_BLOCK ('block') special attribute.
		"""
		logging.debug('OgpElement.__setBlocking(blocking=' + repr(blocking) + ')')
		if blocking:
			self.__attrib[OgpXmlConsts.ATTR_BLOCK] = str(blocking).lower()
		else:
			try:
				del self.__attrib[OgpXmlConsts.ATTR_BLOCK]
			except:
				pass
	blocking = property(__getBlocking, __setBlocking)

	def delElements(self):
		"""
			Removes any child
		"""
		logging.debug('OgpElement.delElements()')
		for e in self:
			self.remove(e)

	def __checkUnicity(self, elt):
		"""
			Checks if no child element has the same name and the same attributes,
		"""
		logging.debug('OgpElement.__checkUnicity(elt=' + repr(elt) + ')')
		for e in self:
			if e.tag == elt.tag and e.attributes == elt.attributes:
				return False
		return True

	def append(self, newChild):
		"""
			Works as the standard function, but if newChild is an Element, 
			checks unicity before adding, and deletes text
		"""
		logging.debug('OgpElement.append(newChild=' + repr(newChild) + ')')
		if (not self.__checkUnicity(newChild)):raise OgpXmlError('append: element is not unique.')
		self.text = None
		ElementBase.append(self, newChild)

	def insert(self, index, newChild):
		"""
			Works as the standard function, but if newChild is an Element,  
			checks unicity before adding, and deletes text.
		"""
		logging.debug('OgpElement.insert(index=' + repr(index) + ', newChild=' + repr(newChild) + ')')
		if (not self.__checkUnicity(newChild)):raise OgpXmlError('insert: element is not unique.')
		self.text = None
		ElementBase.insert(self, index, element)

	def extend(self, elements):
		"""
			Works as the standard function, but if newChild is an Element, 
			checks unicity before adding, and deletes text.
		"""
		logging.debug('OgpElement.extend(elements=' + repr(elements) + ')')
		for element in elements:
			if (not self.__checkUnicity(element)):raise OgpXmlError('extend: element is not unique.')
		self.text = None
		ElementBase.extend(self, elements) 

	def set(self, name, value):
		"""
			Works as the standard function, but if newChild is an Element, 
			checks that self will still be unique after setting the attribute.
		"""
		logging.debug('OgpElement.set(name=' + repr(name) + ', value=' + repr(value) + ')')
		#Computation of new attribute list
		newattrs=self.attributes
		newattrs[name] = value
		
		#check if no brother element has the future attribute set	
		parent = self.getparent()
		if parent is not None:
			for br in parent:
				if br is not self and br.tag == self.tag and br.attributes == newattrs:
					raise OgpXmlError('set: element would no more be unique.')
		self.__attrib[name] = value

	def merge(self, peer):
		"""
			Merges self with peer. Peer is considered as the "child" conf (LDAP speaking), so that it has precendence on self.
			See plugin documentation for further details on the algorithm
		"""
		logging.debug('OgpElement.merge()')
		#if self and peer are not exactly the same (i.e. same name and same attributes),
		#raise OgpXmlError.
		if self.tag != peer.tag or self.attributes != peer.attributes:
			raise OgpXmlError('merge: peer has not same name or attributes.')
		
		#Nodes must have same content. If not, raise OgpXmlError
		if ((len(self) == 0) ^ (len(peer) == 0)) and ((self.text is None) ^ (peer.text is None)):
			raise OgpXmlError('merge: peer has not same type of content.\nself: ' + self.toString() + '\npeer: ' + peer.toString())

		#if blocking, stop here
		if self.blocking:return

		#First case : nodes contains Text
		if self.text is not None or peer.text is not None:
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
		logging.debug('OgpElement.__reorder_ids(peer=' + repr(peer) + ')')
		peerMaxId = 0
		if len(peer) > 0 and len(self) > 0:
			for e in peer:
				id = e.get(OgpXmlConsts.ATTR_ID)
				if id is not None and int(id) > peerMaxId:
					peerMaxId = int(id)

			for e in self:
				id = e.get(OgpXmlConsts.ATTR_ID)
				if id is not None:
					e.set(OgpXmlConsts.ATTR_ID, str(int(id) + peerMaxId + 1))

	def toString(self, xsl=None, params=None):
		logging.debug('OgpElement.__reorder_ids(xsl=' + repr(xsl) + ', params=' + repr(params) + ')')
		if xsl is None:
			return tostring(self)
		else:
			self.__processXsl(xsl, params)

	def __processXsl(self, xsl, params):
		logging.debug('OgpElement.__processXsl(xsl=' + repr(xsl) + ', params=' + repr(params) + ')')
		transform = XSLT(xsl)
		if params is None:
			return str(transform(self))
		else:
			return str(transform(self), params)

	def __makePlugin(name, fileNames):
		"""
			Creates a standard XML plugin tree, with the specified <file> sections
			name: the plugin name
			fileNames: the list of the desired files
		"""
		logging.debug('OgpElement.__makePlugin(name=' + repr(name) + ', fileNames=' + repr(fileNames) + ')')
		res = Element(OgpXmlConsts.TAG_PLUGIN)
		res.set(OgpXmlConsts.ATTR_PLUGIN_NAME, name)
		res.append(Element(OgpXmlConsts.TAG_CONF))
		files_e = Element(OgpXmlConsts.TAG_FILES)
		res.append(files_e)
		for f in fileNames:
			f_e = OgpElement.makeFile(f)
			files_e.append(f_e)
		return res
	makePlugin = staticmethod(__makePlugin)

	def __makeFile(name):
		"""
			Creates a standard XML file tree.
			name: the file name
		"""
		logging.debug('OgpElement.__makeFile(name=' + repr(name) + ')')
		res = Element(OgpXmlConsts.TAG_FILE)
		res.set(OgpXmlConsts.ATTR_FILE_NAME, name)
		res.append(Element(OgpXmlConsts.TAG_CONF))
		res.append(Element(OgpXmlConsts.TAG_SECURITY))
		return res
	makeFile = staticmethod(__makeFile)

class OgpXmlError(Exception):
	"""
		OGP XML error class.
	"""
	def __init__(self, value):
		self.value = value
		logging.error(str(self))
	
	def __str__(self):
					return repr("OgpXmlError: " + self.value)

class OgpElementClassLookup(PythonElementClassLookup):
	"""
		Standard OgpElement "factory"
	"""
	def lookup(self, document, element):
		return OgpElement
