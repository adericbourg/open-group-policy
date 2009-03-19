#!/usr/bin/python
# -*- coding: utf-8 -*

import ldap
import ldap.modlist as modlist
from ldap.dn import *
from ogpldapconsts import *
from lxml.etree import *
from ogp.etree import *

class OgpCore(object):
	"""
		Provides LDAP acces methods
		Initialisation: OgpCore(uri, dn, passwd, certs)
			uri: ldap://host:port
			dn: user dn
			passwd: user password
			certs: path to certs files (.pem)
		Usage: OgpCore.getInstance().[method]([args])
	"""
	
	__instance = None

	def __init__(self, uri, dn=None, passwd=None, certs=None):
		"""
			Creates singleton instance
		"""
		# Check whether we already have an instance
		if OgpCore.__instance is None:
			# Create and remember instance
			OgpCore.__instance = OgpCore.__ogpcore(uri, dn, passwd, certs)
		# Store instance reference as the only member in the handle
		self.__dict__['OgpCore__instance'] = OgpCore.__instance

	def __getattr__(self, attr):
		#	Delegate access to implementation
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		# Delegate access to implementation
		return setattr(self.__instance, attr, value)

	def getInstance():
		"""
			Returns the core unique instance
		"""
		return OgpCore.__instance
	getInstance = staticmethod(getInstance)
	
	class __ogpcore:

		def	__init__(self, uri, dn=None, passwd=None, certs=None):
			"""
				Initlializes connection to LDAP server. 
				uri: ldap://host:port
				dn: user dn
				passwd: user password
				certs: path to certs files (.pem)
			"""
			self.l = ldap.initialize(uri)
			self.l.simple_bind_s(dn, passwd)

		def __del__(self):
			#close LDAP connection before deleting the object
			self.l.unbind_s()

		def createOU(self, dn, description=None):
			"""
				Creates an oGPOrganizationalUnit LDAP object and initializes it.
				dn: the distinguished name of the targeted object
				description (optionnal): an optional description of the object
			"""
			attrs = {}
			attrs['objectclass'] = OgpLDAPConsts.OBJECTCLASS_OU
			attrs[OgpLDAPConsts.ATTR_OGPSOA] = OgpLDAPConsts.VALUE_OGPSOA
			if description is not None:
				attrs[OgpLDAPConsts.ATTR_DESCRIPTION] = description
			attrs[OgpLDAPConsts.ATTR_CONFIG] = OgpLDAPConsts.VALUE_CONFIG
			self.__add(dn, attrs) 

		def createMachine(self, dn, others={}):
			"""
				Creates an oGPComputer LDAP object and initializes it.
				dn: the distinguished name of the targeted object
				others (optionnal) : other LDAP attributes
			"""
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

		def deleteDN(self, dn, fullTree=False):
			"""
				Deletes an LDAP object
				dn: the distinguished name of the targeted object
				fullTree: if set to True, deletion is recursive
			"""
			if fullTree: #recursively delete direct children before deleting dn itself
				tree = self.l.search_s(dn, ldap.SCOPE_SUBTREE, '(objectclass=*)' ,[''])
				for e in tree:
					if len(str2dn(e[0])) == (len(str2dn(dn)) + 1):
						self.deleteDN(e[0], fullTree=True)
			self.__delete(dn)

		def pullAttributes(self, dn, attrs):
			"""
				Returns a dict containing the requested attributes
				dn: the distinguished name of the targeted object
				attrs: a list containing the requested attributes' names
			"""
			return self.l.search_s(dn, ldap.SCOPE_BASE, attrlist=attrs)[0][1]

		def pushDescription(self, dn, description):
			"""
				Sets the OgpLDAPConsts.ATTR_DESCRIPTION LDAP attribute
				dn: the distinguished name of the targeted object
				description: the description
			"""
			mods = [(ldap.MOD_REPLACE, OgpLDAPConsts.ATTR_DESCRIPTION, description)]
			self.__modify(dn, mods)

		def pullPluginConf(self, dn, pluginName, fullTree=False):
			"""
				Retrieves the XML tree containing the configuration for a given plugin and a given DN.
				The root of the returned XML tree is <plugin name="[pluginName]">.
				dn: the distinguished name of the targeted object
				pluginName: the targeted plugin name
				fullTree: if set to True, merges the conf from the baseDN up to the given DN
			"""
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

		def pushPluginConf(self, dn, pluginConf):
			"""
				Stores the plugin configuration in the LDAP and updates the SOA.
				dn: the distinguished name of the targeted object
				pluginConf: a XML tree reprensenting the XML configuration. Its root must be <plugin name="[pluginName]">
			"""
			#replace current <plugin name="..." /> entry
			pluginName = pluginConf.get(OgpXmlConsts.ATTR_PLUGIN_NAME)
			currentConf = self.__pullConf(dn)
			for p in currentConf:
				if p.get(OgpXmlConsts.ATTR_PLUGIN_NAME) == pluginName:
					currentConf.remove(p)
					break
			currentConf.append(pluginConf)
			strConf = currentConf.toString()

			#get SOA
			currentSOA = self.__pullSOA(dn)
			#commit Changes
			mods = [ 
				(ldap.MOD_REPLACE, OgpLDAPConsts.ATTR_CONFIG, strConf),
				(ldap.MOD_REPLACE, OgpLDAPConsts.ATTR_OGPSOA, str(currentSOA + 1))
			]
			self.__modify(dn, mods)

		def pullSOAs(self, dn):
			"""
				Returns a dict containing all the oGPSOA attributes from the baseDN up to the targeted object.
				dn: the distinguished name of the targeted object
			"""
			SOAs = {}
			dn=str2dn(dn)
			dn.reverse()
			loopDn=[]
			for obj in dn:
				loopDn.insert(0, obj)
				print dn2str(loopDn)
				try:
					SOAs[dn2str(loopDn)] = self.__pullSOA(dn2str(loopDn))
					print dn2str(loopDn) + SOAs[dn2str(loopDn)]
				except:
					pass
			return SOAs
		
		def __add(self, dn, attrs):
			ldif = modlist.addModlist(attrs)
			self.l.add_s(dn,ldif)

		def __modify(self, dn, mods):
			self.l.modify_s(dn,mods)

		def __delete(self, dn):
			self.l.delete_s(dn)

		def __pullConf(self, dn):
			return fromstring(self.pullAttributes(dn,[OgpLDAPConsts.ATTR_CONFIG])[OgpLDAPConsts.ATTR_CONFIG], OGP_PARSER)

		def __pullSOA(self, dn):
			return int(self.pullAttributes(dn, [OgpLDAPConsts.ATTR_OGPSOA])[OgpLDAPConsts.ATTR_OGPSOA])
		
