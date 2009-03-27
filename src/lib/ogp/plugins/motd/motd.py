#!/usr/bin/python
# -*- coding: utf-8 -*

from ogp.plugins.plugin import *
from os import spawnl, P_WAIT
import logging

class Motd(Plugin):
	name = "motd"
	files = ['motd', 'motd.tail']
	__motd_xpath = OgpXmlConsts.TAG_FILES + "/" + OgpXmlConsts.TAG_FILE + \
			"[@" + OgpXmlConsts.ATTR_FILE_NAME + "='motd']" 
	__conf_xpath = OgpXmlConsts.TAG_CONF 
	__distro_xpath = OgpXmlConsts.TAG_CONF + "/distro" 

	def pushFile(self, file, content, blocking=False):
		logging.debug('Motd.pushFile(file=' + repr(file) + ', content=' + repr(content) + ', blocking=' + repr(blocking) + ')')
		logging.debug('Motd: pushing file ' + repr(file) + '(blocking=' + repr(blocking) + ')')
		if file == 'motd.tail':
			logging.warning('Motd.pushFile: motd.tail should not be edited! Editing motd...')
			file = 'motd'

		if file == 'motd':
			file_e = self.currentConf.xpath(self.__motd_xpath + '/' + OgpXmlConsts.TAG_CONF)[0]
			file_e.text = content
			file_e.blocking = blocking

	def pullFile(self, file, fullTree=False):
		logging.debug('Motd.pullFile(file=' + repr(file) + ', fullTree=' + repr(fullTree) + ')')
		if fullTree:
			parentConf = self.core.pullPluginConf(self.parentDn, self.name, fullTree=True)
			if parentConf is None:
				parentConf = OgpElement.makePlugin(self.name, self.files)
			parentConf.merge(self.currentConf)
			return parentConf.xpath(self.__motd_xpath + '/' + OgpXmlConsts.TAG_CONF)[0].text
		else:
			return self.currentConf.xpath(self.__motd_xpath + '/' + OgpXmlConsts.TAG_CONF)[0].text

	def help(self, cmdName=None):
		logging.debug('Motd.help(cmdName=' + repr(cmdName) + ')')
		if cmdName is None:
			return {'setdistro': "Sets distribution name."}
		elif cmdName == 'setdistro':
			return {'distro': "(string) If set to 'debian', will install to /etc/motd.tail instead of /etc/motd.", 
					'blocking': "(bool, optionnal) Do not allow inheritance."}
		else:
			raise OgpPluginError('help: unknown command (' + cmdName + ')')

	def runCommand(self, cmdName, argv):
		logging.debug('Motd.runCommand(cmdName=' + repr(cmdName) + ', argv=' + repr(argv) + ')')
		logging.info('Motd: running command ' + repr(cmdName) + '(arguments: ' + repr(argv) + ')')
		if cmdName != 'setdistro':
			raise OgpPluginError('runCommand: unknown command (' + cmdName + ')')
		else:
			distro = argv['distro']
			try:
				blocking = argv['blocking']
			except:
				blocking = False
			dist_e = self.currentConf.xpath(self.__distro_xpath)
			if len(dist_e) == 0:
				dist_e = Element('distro')
				conf_e = self.currentConf.xpath(self.__conf_xpath)[0]
				conf_e.append(dist_e)
			else:
				dist_e = dist_e[0]
			dist_e.text = distro
			dist_e.blocking = blocking

	def installConf(self):
		logging.debug('Motd.installConf()')
		logging.info('Motd: installing conf.')
		motd = str(self.pullFile('motd', True))
		dist_e = self.currentConf.xpath(self.__conf_xpath + '/distro')
		if len(dist_e) != 0:
			distro = dist_e[0].text
		else:
			distro = None

		print distro
		
		prefix = '/etc/'

		if distro == 'debian':
			f = open(prefix + 'motd.tail','w')
			f.write(motd)
			f.close()
			spawnl(P_WAIT, prefix + 'init.d/bootmisc.sh', 'start')
			self.setSecurityAttributes('motd', prefix + 'motd.tail')
		else:
			f = open(prefix + 'motd', 'w')
			f.write(motd)
			f.close()

		self.setSecurityAttributes('motd', prefix + 'motd')

