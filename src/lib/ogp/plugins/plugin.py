#!/usr/bin/python
# -*- coding: utf-8 -*

def setattr(self, item, value):
	"""
		Plugin class and metaclass __setattr__ method
		Throws an exception when attempting to modify the plugin name.
	"""
	if item == "name":
		raise OgpPluginError('__setattr__: name is readonly.')
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
	
	__metaclass__ = M_Plugin
	
	def __init__(self, dn):
		self.__dn = dn
	
	__setattr__ = setattr # Plugin name protection

	name = None # the plugin name
	__registeredPlugins = dict()
	
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
		pass

	def cancel(self):
		"""
			Do not commit and discard changes.
		"""
		pass

	def chown(self, filename, uid=None, gid=None):
		"""
			Changes owner, changes the user and/or group ownership of 
			the given file
		"""
		#TODO
		pass

	def chmod(self, filename, uw, ux, us, gs, t):
		"""
			Changes the permissions of the given file according to mode
		"""
		#TODO
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

	def pushFile(self, file, content):
		"""
			Builds XML configuration from a string content and loads it in the corresponding <file> Element
			Arguments:
				file   : the logical name of the targeted file
				content: the content of the file
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
