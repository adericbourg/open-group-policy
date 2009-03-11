#!/usr/bin/python
# -*- coding: utf-8 -*

from Metaclass import Metaclass
from AbstractMethod import AbstractMethod

class Plugin (object):
	__metaclass__ = Metaclass

	def __init__(self, dn):
		self.__dn = dn

	def getPluginFromName(plugin):
		return
	getPluginFromName = staticmethod('getPluginFromName')
	
	# Abstract methods
	#mergeDescription = AbstractMethod('mergeDescription')

	def getName():
		return ""

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

