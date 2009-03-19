#!/usr/bin/python
# -*- coding: utf-8 -*

from ogp.plugins.plugin import *

class Test(Plugin):
	name = "test"
	def test(self):
		print "toto" + self.name
