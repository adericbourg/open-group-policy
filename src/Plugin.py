#!/usr/bin/python
# -*- coding: utf-8 -*

import Metaclass
import AbstractMethod

class Plugin (object):
	__metaclass__ = Metaclass

	getPluginFromName = staticmethod('getPluginFromName')
	def getPluginFromName(plugin):
		pass
	
	# Abstract methods
	mergeDescription = AbstractMethod('mergeDescription')
	toString = AbstractMethod('toString')
	toXML = AbstractMethode('toXML')

	def getName():
		pass

	def mergeFile(parentFile, childFile):
		pass

	def mergeSecurity(parentSecurity, childSecurity):
		pass
