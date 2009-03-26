#!/usr/bin/python
# -*- coding: utf-8 -*

import ldap
import ldap.modlist as modlist
from ldap.dn import *
from ogpldapconsts import *
from lxml.etree import *
from ogp.etree import *
import logging
import sys
from hashlib import sha1
from base64 import standard_b64encode
from pkg_resources import resource_filename
from os.path import dirname,join

XML_SCHEMA="ogpxmlconfig.xsd"

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
		logging.debug('OgpCore.__init__(uri=' + repr(uri) + ', dn=' + repr(dn) + ', passwd=****, certs=[not implemented])')
		# Check whether we already have an instance
		if OgpCore.__instance is None:
			# Create and remember instance
			logging.info('OgpCore: connecting to ' + repr(uri) + ' with dn=' + repr(dn) + '...')
			try:
				OgpCore.__instance = OgpCore.__ogpcore(uri, dn, passwd, certs)
			except:
				logging.error('OgpCore: initialization failed with ' + repr(sys.exc_info()[1]) + '.')
				OgpCore.__instance = None
				raise
		else:
			logging.warning('OgpCore: already connected!')
		# Store instance reference as the only member in the handle
		self.__dict__['OgpCore__instance'] = OgpCore.__instance

	def __getattr__(self, attr):
		logging.debug('OgpCore.__getattr__(attr=' + repr(attr) + ')')
		#	Delegate access to implementation
		return getattr(self.__instance, attr)

	def __setattr__(self, attr, value):
		logging.debug('OgpCore.__setattr__(attr=' + repr(attr) + ', value=' + repr(value) + ')')
		# Delegate access to implementation
		return setattr(self.__instance, attr, value)

	def __del__(self):
		logging.debug('OgpCore.__del__()')
		OgpCore.__instance = None

	def getInstance():
		"""
			Returns the core unique instance
		"""
		logging.debug('OgpCore.getInstance()')
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
			logging.debug('OgpCore.__ogpcore.__init__(uri=' + repr(uri) + ', dn=' + repr(dn) + ', passwd=****, certs=[not implemented])')
			self.l = ldap.initialize(uri)
			self.l.simple_bind_s(dn, passwd)
			path = dirname(resource_filename(__name__, '__init.py__'))
			schema_f=open(join(path, XML_SCHEMA))
			self.__schema = etree.XMLSchema(parse(schema_f))
			close(f)

		def __del__(self):
			logging.debug('OgpCore.__ogpcore.__del__()')
			#close LDAP connection before deleting the object
			self.l.unbind_s()

		def createOU(self, dn, description=None, others={}):
			"""
				Creates an oGPOrganizationalUnit LDAP object and initializes it.
				dn: the distinguished name of the targeted object
				description (optionnal): an optional description of the object
			"""
			logging.debug('OgpCore.__ogpcore.createOU(dn=' + repr(dn) + 'description=' + repr(description) + ', others=' + repr(others) + ')')
			if description is not None:
				logging.info('OgpCore: creating organizational unit  ' + repr(dn) + '( ' + description + ')')
			else:
				logging.info('OgpCore: creating organizational unit  ' + repr(dn) + '.')
			
			attrs = others
			attrs['objectclass'] = OgpLDAPConsts.OBJECTCLASS_OU
			attrs[OgpLDAPConsts.ATTR_OGPSOA] = OgpLDAPConsts.VALUE_OGPSOA
			if description is not None:
				attrs[OgpLDAPConsts.ATTR_DESCRIPTION] = description
			attrs[OgpLDAPConsts.ATTR_CONFIG] = OgpLDAPConsts.VALUE_CONFIG
			self.__add(dn, attrs) 

		def createMachine(self, dn, passwd, description=None, others={}):
			"""
				Creates an oGPComputer LDAP object and initializes it.
				dn: the distinguished name of the targeted object
				passwd: the cleartext password for the machine
				description (optionnal): an optional description of the object
				others (optionnal) : other LDAP attributes
			"""
			logging.debug('OgpCore.__ogpcore.createMachine(dn=' + repr(dn) + ', others=' + repr(others) + ')')
			if description is not None:
				logging.info('OgpCore: creating organizational unit  ' + repr(dn) + '( ' + description + ')')
			else:
				logging.info('OgpCore: creating organizational unit  ' + repr(dn) + '.')
			
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
			s=sha1()
			s.update(passwd)
			attrs[OgpLDAPConsts.ATTR_USERPASSWORD] = "{SHA}" + standard_b64encode(s.digest())
			
			attrs[OgpLDAPConsts.ATTR_CONFIG] = OgpLDAPConsts.VALUE_CONFIG
			if description is not None:
				attrs[OgpLDAPConsts.ATTR_DESCRIPTION] = description

			self.__add(dn, attrs)

		def deleteDN(self, dn, fullTree=False):
			"""
				Deletes an LDAP object
				dn: the distinguished name of the targeted object
				fullTree: if set to True, deletion is recursive
			"""
			logging.debug('OgpCore.__ogpcore.deleteDn(dn=' + repr(dn), 'fullTree=' + repr(fullTree) + ')')
			logging.info('OgpCore: deleting ' + repr(dn) + '(recursive: ' + repr(fullTree) + ').')
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
			logging.debug('OgpCore.__ogpcore.pullAttributes(dn=' + repr(dn), 'attrs=' + repr(attrs) + ')')
			return self.l.search_s(dn, ldap.SCOPE_BASE, attrlist=attrs)[0][1]

		def pushDescription(self, dn, description):
			"""
				Sets the OgpLDAPConsts.ATTR_DESCRIPTION LDAP attribute
				dn: the distinguished name of the targeted object
				description: the description
			"""
			logging.debug('OgpCore.__ogpcore.pushDescription(dn=' + repr(dn), 'description=' + repr(description) + ')')
			logging.info('OgpCore: pushing description on ' + repr(dn) + '(description: ' + repr(fullTree) + ').')
			mods = [(ldap.MOD_REPLACE, OgpLDAPConsts.ATTR_DESCRIPTION, description)]
			self.__modify(dn, mods)

		def pushPasswd(self, dn, passwd):
			"""
				Sets the OgpLDAPConsts.ATTR_USERPASSWORD LDAP attribute
				dn    : the distinguished name of the targeted object
				passwd: the cleartext password
			"""
			logging.debug('OgpCore.__ogpcore.pushPasswd(dn=' + repr(dn), 'passwd=****)')
			logging.info('OgpCore: pushing userPasword on ' + repr(dn) + '.')
			s=sha1()
			s.update(passwd)
			mods = [(ldap.MOD_REPLACE, OgpLDAPConsts.ATTR_DESCRIPTION, "{SHA}" + standard_b64encode(s.digest()))]
			self.__modify(dn, mods)

		def pullPluginConf(self, dn, pluginName, fullTree=False):
			"""
				Retrieves the XML tree containing the configuration for a given plugin and a given DN.
				The root of the returned XML tree is <plugin name="[pluginName]">.
				dn: the distinguished name of the targeted object
				pluginName: the targeted plugin name
				fullTree: if set to True, merges the conf from the baseDN up to the given DN
			"""
			logging.debug('OgpCore.__ogpcore.pullPluginConf(dn=' + repr(dn) + 'pluginName=' + repr(pluginName) + ', fullTree=' + repr(fullTree) + ')')
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
					xpath_arg = "/" + OgpXmlConsts.TAG_OGP + "/" + OgpXmlConsts.TAG_PLUGIN + "[@" + OgpXmlConsts.ATTR_PLUGIN_NAME  + "='" + pluginName +"']"
					pConf = self.__pullConf(dn).xpath(xpath_arg)[0]
				except:
					return None
				
			return pConf

		def pushPluginConf(self, dn, pluginConf):
			"""
				Stores the plugin configuration in the LDAP and updates the SOA.
				dn: the distinguished name of the targeted object
				pluginConf: a XML tree reprensenting the XML configuration. Its root must be <plugin name="[pluginName]">
			"""
			logging.debug('OgpCore.__ogpcore.pushPluginConf(dn=' + repr(dn) + 'pluginConf=' + pluginConf.toString() + ')')
			#replace current <plugin name="..." /> entry
			pluginName = pluginConf.get(OgpXmlConsts.ATTR_PLUGIN_NAME)
			logging.info('OgpCore: pushing conf for plugin ' + pluginName + ' on ' + repr(dn) + '.')
			currentConf = self.__pullConf(dn)
			for p in currentConf:
				if p.get(OgpXmlConsts.ATTR_PLUGIN_NAME) == pluginName:
					currentConf.remove(p)
					break
			currentConf.append(pluginConf)
			#validates against schema
			if not self.__schema.validate(currentConf):
				raise OgpCoreError('validation failed when pushing conf for plugin' + pluginName + '.')
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
			logging.debug('OgpCore.__ogpcore.pullSOAs(dn=' + repr(dn) + ')')
			SOAs = {}
			dn=str2dn(dn)
			dn.reverse()
			loopDn=[]
			for obj in dn:
				loopDn.insert(0, obj)
				try:
					SOAs[dn2str(loopDn)] = self.__pullSOA(dn2str(loopDn))
				except:
					pass
			return SOAs

		def getRequiredPlugins(self, dn):
			"""
				Returns the names of the plugins that should be installed on the client,
				identified by its DN, to install the configuration store in the LDAP.
				dn: the distinguished name of the targeted object
			"""
			logging.debug('OgpCore.__ogpcore.getRequiredPlugins(dn=' + repr(dn) + ')')
			plugins = []
			dn=str2dn(dn)
			dn.reverse()
			loopDn=[]
			for obj in dn:
				loopDn.insert(0, obj)
				try:
					conf = self.__pullConf(dn2str(loopDn))
					for plugin in conf:
						if plugin.get(OgpXmlConsts.ATTR_PLUGIN_NAME) not in plugins:
							plugins.append(plugin.get(OgpXmlConsts.ATTR_PLUGIN_NAME))
				except:
					pass
			plugins.sort()
			return plugins
		
		def __add(self, dn, attrs):
			logging.debug('OgpCore.__ogpcore.__add(dn=' + repr(dn) + ', attrs=' + repr(attrs) + ')')
			try:
				ldif = modlist.addModlist(attrs)
				self.l.add_s(dn,ldif)
			except:
				logging.error('OgpCore: __add failed with ' + repr(sys.exc_info()[1]) + '.')
				raise

		def __modify(self, dn, mods):
			logging.debug('OgpCore.__ogpcore.__modify(dn=' + repr(dn) + ', mods=' + repr(mods) + ')')
			try:
				self.l.modify_s(dn,mods)
			except:
				logging.error('OgpCore: __modify failed with ' + repr(sys.exc_info()[1]) + '.')
				raise

		def __delete(self, dn):
			logging.debug('OgpCore.__ogpcore.__delete(dn=' + repr(dn) + ')')
			try:
				self.l.delete_s(dn)
			except:
				logging.error('OgpCore: __delete failed with ' + repr(sys.exc_info()[1]) + '.')
				raise

		def __pullConf(self, dn):
			logging.debug('OgpCore.__ogpcore.__pullConf(dn=' + repr(dn) + ')')
			try:
				return fromstring(self.pullAttributes(dn,[OgpLDAPConsts.ATTR_CONFIG])[OgpLDAPConsts.ATTR_CONFIG][0], OGP_PARSER)
			except KeyError:
				logging.info('OgpCore: no conf at dn=%s' % repr(dn))
				return None
			except:
				logging.error('OgpCore: __pullConf failed with ' + repr(sys.exc_info()[1]) + '.')
				raise

		def __pullSOA(self, dn):
			logging.debug('OgpCore.__ogpcore.__pullSOA(dn=' + repr(dn) + ')')
			try:
				return int(self.pullAttributes(dn, [OgpLDAPConsts.ATTR_OGPSOA])[OgpLDAPConsts.ATTR_OGPSOA][0])
			except KeyError:
				logging.info('OgpCore: no conf at dn=%s' % repr(dn))
				return None
			except:
				logging.error('OgpCore: __pullSOA failed with ' + repr(sys.exc_info()[1]) + '.')
				raise

class OgpCoreError(Exception):
				  """
    OGP plugin error class.
  """
  def __init__(self, value):
					    self.value = value
    logging.error(str(self))

  def __str__(self):
					    return repr("OgpCoreError: " + self.value)

