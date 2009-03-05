#!/usr/bin/python
# -*- coding: utf-8 -*

from Metaclass import Metaclass
from AbstractMethod import AbstractMethod

class Plugin (object):
	__metaclass__ = Metaclass

	getPluginFromName = staticmethod('getPluginFromName')
	def getPluginFromName(plugin):
		pass
	
	# Abstract methods
	mergeDescription = AbstractMethod('mergeDescription')
	toString = AbstractMethod('toString')
	toXML = AbstractMethod('toXML')

	def getName():
		return ""

	def mergeFile(parentFile, childFile):
		pass

	def mergeSecurity(parentSecurity, childSecurity):
		pass
