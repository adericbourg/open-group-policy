#!/usr/bin/python
# -*- coding: utf-8 -*

import ldap
import ldap.modlist as modlist
from OgpLDAPConsts import *

class OgpCore(object):

	__instance = None

	def __init__(self, uri, dn=None, passwd=None, cert=None):
		""" Create singleton instance """
		# Check whether we already have an instance
		if OgpCore.__instance is None:
			# Create and remember instance
			OgpCore.__instance = OgpCore.__ogpcore(uri, dn, passwd, cert)
		# Store instance reference as the only member in the handle
		self.__dict__['OgpCore__instance'] = OgpCore.__instance

	def __getattr__(self, attr):
		""" Delegate access to implementation """
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		""" Delegate access to implementation """
		return setattr(self.__instance, attr, value)

	
	class __ogpcore:

		def	__init__(self, uri, dn=None, passwd=None, cert=None):
			"""
				Initlialize connection to LDAP server. 
				uri: ldap://host:port
				dn: usdr dn
				passwd: user password
				cert: path to cert file (.pem)
			"""
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

		def push(self, plugin, dn, overwrite):
			pass

		def pull(self, ou, recursive):
			pass

		def pullPlugin(self, ou, plugin, recursive):
			pass

		def getFileList(self, ou, recursive):
			pass

		def build(self, ou, recursive):
			pass

		def buildFile(self, ou, recursive):
			pass
