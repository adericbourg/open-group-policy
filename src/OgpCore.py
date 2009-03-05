#!/usr/bin/python
# -*- coding: utf-8 -*

import ldap
import ldap.modlist as modlist
from OgpLDAPConsts import *

class OgpCore:

	def	__init__(self, uri, dn=None, passwd=None, cert=None):
		'''
			Initlialize connection to LDAP server. 
			uri: ldap://host:port
			dn: usdr dn
			passwd: user password
			cert: path to cert file (.pem)
		'''
		self.l = ldap.initialize(uri)
		self.l.simple_bind_s(dn, passwd)

	def __del__(self):
		self.l.unbind_s()

	def createOU(self, dn, description=None):
		attrs = {}
		attrs['objectclass'] = OgpLDAPConsts.OBJECTCLASS_OU
		attrs[OgpLDAPConsts.ATTR_OGPSOA] = OgpLDAPConsts.VALUE_OGPSOA
		attrs[OgpLDAPConsts.ATTR_DESCRIPTION] = description
		attrs[OgpLDAPConsts.ATTR_CONFIG] = OgpLDAPConsts.VALUE_CONFIG
		self.__add(dn, attrs) 

	def __add(self, dn, attrs):
		ldif = modlist.addModlist(attrs)
		self.l.add_s(dn,ldif)

	def createMachine(self, dn, others={}):
		attrs = others
		attrs['objectClass'] = OgpLDAPConsts.OBJECTCLASS_MACHINE
		attrs[OgpLDAPConsts.ATTR_OGPSOA] = OgpLDAPConsts.VALUE_OGPSOA
		try:
			attrs[OgpLDAPConsts.ATTR_SAMACCOUNTNAME]
		except:
			attrs[OgpLDAPConsts.ATTR_SAMACCOUNTNAME] = OgpLDAPConsts.VALUE_SAMACCOUNTNAME
		try:
			attrs[OgpLDAPConsts.ATTR_OBJECTSID]
		except:
			attrs[OgpLDAPConsts.ATTR_OBJECTSID] = OgpLDAPConsts.VALUE_OBJECTSID
		attrs[OgpLDAPConsts.ATTR_CONFIG] = OgpLDAPConsts.VALUE_CONFIG
		self.__add(dn, attrs)

	def push(self, file, dn, overwrite):
		pass

	def pull(self, ou, recursive):
		pass

	def pullFile(self, ou, file, recursive):
		pass

	def getFileList(self, ou, recursive):
		pass

	def build(self, ou, recursive):
		pass

	def buildFile(self, ou, recusrive):
		pass

