#!/usr/bin/python
# -*- coding: utf-8 -*

from metaclass import Metaclass
from abstractmethod import AbstractMethod

class Plugin(object):
	#__metaclass__ = Metaclass
	def __init__(self, dn):
		self.__dn = dn
	
	__registeredPlugins = dict()
	def __getPluginFromName(name):
		return Plugin.__registeredPlugins[name]
	getPluginFromName = staticmethod(__getPluginFromName)

	def __registerPlugin(pluginClass):
		try:
			Plugin.__registeredPlugins[pluginClass.name]
			raise OgpPluginError("registerPlugin: duplicated plugin name '" + pluginClass.name + "'")
		except:
			pass
		Plugin.__registeredPlugins[pluginClass.name] = pluginClass
	registerPlugin = staticmethod(__registerPlugin)

	def __getRegisteredPlugins():
		return Plugin.__registeredPlugins.copy()
	getRegisteredPlugins = staticmethod(__getRegisteredPlugins)
	
	# Abstract methods
	#mergeDescription = AbstractMethod('mergeDescription')

	name = None

	def installConf(self):
		pass

	def help(self, cmd):
		pass

	def runCommand(self, argv):
		pass

	def update(self):
		"""
			Commit changes
		"""
		pass

	def cancel(self):
		"""
			Do not commit and delete changes.
		"""
		pass

	def pullFile(self, file, fullTree=False):
		pass

	def pushFile(self, file, content):
		pass

class OgpPluginError(Exception):
	def __init__(self, value):
		assert isinstance(value, str)
		self.value = value
	
	def __str__(self):
		return repr("OgpXmlError: " + self.value)

