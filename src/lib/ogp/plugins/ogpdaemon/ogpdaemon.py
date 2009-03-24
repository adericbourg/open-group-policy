#!/usr/bin/python
# -*- coding: utf-8 -*

from ogp.plugins.plugin import *
from os import spawnl, P_WAIT

class OgpDaemon(Plugin):
	name = "ogpdaemon"
	files = []
	__localParams = ['dn', 'uri', 'passwd']
	__remoteParams = ['timeBetweenUpdates', 'updateOnStartup']
	__conf_xpath = OgpXmlConsts.TAG_CONF 

	def pushFile(self, file, content, blocking=False):
		raise OgpPluginError("pushFile: OgpDaemon has no files! You're useless buddy!")

	def pullFile(self, file, fullTree=False):
		raise OgpPluginError("pullFile: OgpDaemon has no files! You're useless buddy!")

	def help(self, cmdName=None):
		if cmdName is None:
			return {'setparam': "Sets a parameter.",'setparam': "Gets a parameter."}
		elif cmdName == 'setparam':
			return {
					'param': "(string) parameter name.\nAvailable parameters: updateOnStartup, timeBetweenUpdates",
					'value': "(string) parameter value.\nIf param is updateOnStartup, value must be 'True' or 'False'.\nIf param is timeBetweenUpdates, value is a number (in minutes)."
					}
		elif cmdName == 'getparam':
			return {
					'param':"(string) parameter name.\nAvailable parameters: updateOnStartup, timeBetweenUpdates",
					'fullTree':"(optional, bool) merge parameters from base DN to current DN."
					}
		else:
			raise OgpPluginError("help: unknown command '" + cmdName + "'")

	def runCommand(self, cmdName, argv):
		if cmdName == 'setparam':
			self.__setParam(argv['param'], argv['value'])
			return None
		elif cmdName == 'getparam':
			return self.__getParam(argv['param'])
		else:
			raise OgpPluginError("runCommand: unknown command '" + cmdName +"'")

	def installConf(self):
		local = {}
		remote = {}
		for p in self.__localParams:
			local[p] = self.__getParam(p, True)
		for p in self.__remoteParams:
			remote[p] = self.__getParam(p, True)
		return {'local':local,'remote':remote}

	def __getParam(self, param, fullTree=False):
		defaults = {
				'updateOnStartup':'true', 
				'timeBetweenUpdates':'15',
				'dn':None,
				'uri':None,
				'passwd':None
				}
		if (param not in self.__localParams) and (param not in self.__remoteParams):
			raise OgpPluginError("__getParam: unknown parameter '" + param + "'")

		conf = None
		if fullTree:
			conf = self.core.pullPluginConf(self.parentDn, self.name, True)
			if conf is None:
				conf = OgpElement.makePlugin(self.name, self.files)
			conf.merge(self.currentConf)
		else:
			conf = self.currentConf

		xpath = self.__conf_xpath + '/' + param
		param_e = self.currentConf.xpath(xpath)
		if len(param_e) == 0:
			return defaults[param]
		else:
			param_e = param_e[0]
			return param_e.text


	def __setParam(self, param, value):
		if (param not in self.__localParams) and (param not in self.__remoteParams):
			raise OgpPluginError("__setParam: unknown parameter '" + param + "'")
		xpath = self.__conf_xpath + '/' + param
		param_e = self.currentConf.xpath(xpath)
		if len(param_e) == 0:
			param_e = Element(param)
			(self.currentConf.xpath(self.__conf_xpath)[0]).append(param_e)
		else:
			param_e = param_e[0]
		param_e.text = str(value)

