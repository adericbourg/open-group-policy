#!/usr/bin/python
# -*- coding: utf-8 -*

import ldap
import ldap.modlist as modlist
from ldap.dn import *
from ogpldapconsts import *
from lxml.etree import *
from ogp.etree import *


class OgpCore(object):

	__instance = None

	def __init__(self, uri, dn=None, passwd=None, certs=None):
		""" Create singleton instance """
		# Check whether we already have an instance
		if OgpCore.__instance is None:
			# Create and remember instance
			OgpCore.__instance = OgpCore.__ogpcore(uri, dn, passwd, certs)
		# Store instance reference as the only member in the handle
		self.__dict__['OgpCore__instance'] = OgpCore.__instance

	def __getattr__(self, attr):
		""" Delegate access to implementation """
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		""" Delegate access to implementation """
		return setattr(self.__instance, attr, value)

	def getInstance():
		return OgpCore.__instance
	getInstance = staticmethod(getInstance)
	
	class __ogpcore:

		def	__init__(self, uri, dn=None, passwd=None, certs=None):
			"""
				Initlialize connection to LDAP server. 
				uri: ldap://host:port
				dn: usdr dn
				passwd: user password
				certs: path to cert file (.pem)
			"""
			self.l = ldap.initialize(uri)
			self.l.simple_bind_s(dn, passwd)

		def __del__(self):
			self.l.unbind_s()

		def createOU(self, dn, description=None):
			attrs = {}
			attrs['objectclass'] = OgpLDAPConsts.OBJECTCLASS_OU
			attrs[OgpLDAPConsts.ATTR_OGPSOA] = OgpLDAPConsts.VALUE_OGPSOA
			if description is not None:
				attrs[OgpLDAPConsts.ATTR_DESCRIPTION] = description
			attrs[OgpLDAPConsts.ATTR_CONFIG] = OgpLDAPConsts.VALUE_CONFIG
			self.__add(dn, attrs) 

		def deleteDN(self, dn):
			#TODO
			#self.__delete(dn)
			pass


		def __add(self, dn, attrs):
			ldif = modlist.addModlist(attrs)
			self.l.add_s(dn,ldif)

		def __delete(self, dn):
			#TODO
			self.l.delete_s(dn)

		def createMachine(self, dn, others={}):
			attrs = others
			attrs['objectClass'] = OgpLDAPConsts.OBJECTCLASS_MACHINE
			attrs[OgpLDAPConsts.ATTR_OGPSOA] = OgpLDAPConsts.VALUE_OGPSOA
			
			#default values for mandatory fields
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

		def __pullConf(self, dn):
			return fromstring(self.l.search_s(dn, ldap.SCOPE_BASE, attrlist=[OgpLDAPConsts.ATTR_CONFIG])[0][1][OgpLDAPConsts.ATTR_CONFIG][0], OGP_PARSER)

		def pullPluginConf(self, dn, pluginName, fullTree=False):
			pConf = None
			if fullTree:
				dn=str2dn(dn)
				dn.reverse()
				loopDn=[]
				for obj in dn:
					loopDn.insert(0, obj)
					dnConf = self.pullPluginConf(dn2str(loopDn), pluginName)
					if pConf is None:
						pConf = dnConf
					elif dnConf is not None:
						pConf.merge(dnConf)
					else:
						pass
			else:
				try:
					conf=self.__pullConf(dn)
				except:
					return None
				
				for plugin in conf:
					if plugin.get(OgpXmlConsts.ATTR_PLUGIN_NAME) == pluginName:
						pConf = plugin
						break
			return pConf

		def pushPluginConf(self, dn, conf):
			pass

		def pullSOAs(self, dn):
			pass
