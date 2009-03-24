#!/usr/bin/python
# -*- coding: utf-8 -*

from ldap.dn import str2dn, dn2str
from lxml.etree import *
from ogp.core import *


class omitted(object):
	pass

def setattr(self, item, value):
	"""
		Plugin class and metaclass __setattr__ method
		Throws an exception when attempting to modify the plugin name.
	"""
	if item == "name" or item == "files":
		raise OgpPluginError('__setattr__: ' + item + ' is readonly.')
	self.__dict__[item] = value

class M_Plugin(type):
	"""
		Makes the 'name' __CLASS__ attribute readonly.
	"""
	__setattr__ = setattr # Plugin name protection

class Plugin(object):
	"""
		Provides plugins' base class and plugin registration mechanism.
	"""
	
	name = None # the plugin name
	files = []
	__metaclass__ = M_Plugin
	parentDn = None
	currentConf = None
	dn = None
	__core = None
	__registeredPlugins = dict()

	def __init__(self, dn):
		self.__core = OgpCore.getInstance()
		self.dn = dn
		# Dirty but it pleases Michel :-P
		# Loads RW XML conf from LDAP
		self.cancel()
		# Parent DN (to find parent conf)
		self.parentDn = str2dn(dn)
		del self.parentDn[0]
		self.parentDn = dn2str(self.parentDn)
	
	__setattr__ = setattr # Plugin name protection
	
	def __getPluginFromName(name):
		"""
			returns a plugin class from a name.
		"""
		return Plugin.__registeredPlugins[name]
	getPluginFromName = staticmethod(__getPluginFromName)

	def __registerPlugin(pluginClass):
		"""
			Registers a plugin class.
			Plugins should register themselves in their __init__.py using Plugin.registerPlugin([pluginClass]).
		"""
		try:
			Plugin.__registeredPlugins[pluginClass.name]
			raise OgpPluginError("registerPlugin: duplicated plugin name '" + pluginClass.name + "'.")
		except:
			pass
		Plugin.__registeredPlugins[pluginClass.name] = pluginClass
	registerPlugin = staticmethod(__registerPlugin)

	def __getRegisteredPlugins():
		"""
			Returns a dict() containing all the registered plugin classes
		"""
		return Plugin.__registeredPlugins.copy()
	getRegisteredPlugins = staticmethod(__getRegisteredPlugins)
	
	def update(self):
		"""
			Commit changes to LDAP
		"""
		self.__core.pushPluginConf(self.dn, self.currentConf)

	def cancel(self):
		"""
			Do not commit and discard changes.
		"""
		self.currentConf = self.__core.pullPluginConf(self.dn, self.name)
		if self.currentConf is None:
			self.currentConf = OgpElement.makePlugin(self.name, self.files)


	def chown(self, fileName, uid=omitted, gid=omitted, blocking=False):
		"""
			Changes owner, changes the user and/or group ownership of 
			the given file
		"""
		file_e = self.__getFile(fileName)
		sec_e = file_e.xpath(OgpXmlConsts.TAG_SECURITY)[0]

		if uid is not omitted:
			uid_e = sec_e.xpath(OgpXmlConsts.TAG_UID)
			if len(uid_e) != 0:
				uid_e = uid_e[0]
			else:
				uid_e = None
			if uid is None:
				if uid_e is not None:
					sec_e.remove(uid_e)
			else:
				if uid_e is None:
					uid_e = Element(OgpXmlConsts.TAG_UID)
					sec_e.append(uid_e)
				uid_e.text = str(uid)
				uid_e.blocking = blocking

		if gid is not omitted:
			gid_e = sec_e.xpath(OgpXmlConsts.TAG_GID)
			if len(gid_e) != 0:
				gid_e = gid_e[0]
			else:
				gid_e = None
			if gid is None:
				if gid_e is not None:
					sec_e.remove(gid_e)
			else:
				if gid_e is None:
					gid_e = Element(OgpXmlConsts.TAG_GID)
					sec_e.append(gid_e)
				gid_e.text = str(gid)
				gid_e.blocking = blocking

	def __getFile(self, fileName):
		arg = '/' + OgpXmlConsts.TAG_PLUGIN + '/' + OgpXmlConsts.TAG_FILES + '/' + OgpXmlConsts.TAG_FILE + '[@' + OgpXmlConsts.ATTR_FILE_NAME + "='" + fileName + "']"
		try:
			return self.currentConf.xpath(arg)[0]
		except:
			raise OgpPluginError("__getFile: file '" + fileName + "' does not exist")


	def chmod(self, fileName, rights, blocking=False):
		"""
			Changes the permissions of the given file according to mode
		"""
		file_e = self.__getFile(fileName)
		sec_e = file_e.xpath(OgpXmlConsts.TAG_SECURITY)[0]
		for tag in rights:
			if tag in OgpXmlConsts.TAGS_SECURITY:
				tag_e = sec_e.xpath(tag)
				if len(tag_e) != 0:
					tag_e = tag_e[0]
				else:
					tag_e = None
				if rights[tag] is None:
					if tag_e is not None:
						sec_e.remove(tag_e)
				else:
					if tag_e is None:
						tag_e = Element(tag)
						sec_e.append(tag_e)
					tag_e.text = str(rights[tag])
			else:
				#TODO: log!
				pass

	# Abstract methods
	def installConf(self):
		"""
			Computes the configuration files and install them
		"""
		raise NotImplementedError('This method should be overriden in derived classes.')
	
	def help(self, cmdName=None):
		"""
			provides informations about the plugin user interface.
			plugin.help() should return all available commands as a dict {cmdName: description}
			plugin.help(cmdName) should return all available arguments as a dict {argName: description}
		"""
		raise NotImplementedError('This method should be overriden in derived classes.')

	def runCommand(self, cmdName, argv):
		"""
			Runs a command on the conf.
			Usage:
				plugin.runCommand(cmdName, argv)
				where argv is a dict {argName: argVal}
		"""
		raise NotImplementedError('This method should be overriden in derived classes.')
	
	def pullFile(self, file, fullTree=False):
		"""
			Builds the content of a file from the XML tree, for preview purposes.
			Arguments:
				file          : the logical name of the targeted file
				fullTree=False: if set to true, merges the conf from the baseDN up to the current DN before building
		"""
		raise NotImplementedError('This method should be overriden in derived classes.')

	def pushFile(self, file, content, blocking=False):
		"""
			Builds XML configuration from a string content and loads it in the corresponding <file> Element
			Arguments:
				file    : the logical name of the targeted file
				content : the content of the file
				blocking: sets the block attribute on the targeted file
		"""
		raise NotImplementedError('This method should be overriden in derived classes.')

class OgpPluginError(Exception):
	"""
		OGP plugin error class.
	"""
	def __init__(self, value):
		assert isinstance(value, str)
		self.value = value
	
	def __str__(self):
		return repr("OgpPluginError: " + self.value)
