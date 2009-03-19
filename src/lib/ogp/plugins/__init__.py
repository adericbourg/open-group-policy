#!/usr/bin/python
# -*- coding: utf-8 -*

from plugin import *
from pkg_resources import resource_filename
from os.path import dirname,isdir,join
from os import listdir
from imp import *
from sys import stderr

# Load plugins
path = dirname(resource_filename(__name__, '__init.py__'))
for d in listdir(path):
	if isdir(join(path,d)):
		try:
			load_package('ogp.plugins.' + d,join(path,d))
		except:
			stderr.write("ogp.plugins warning: failed to load plugin '" + d + "'.\n")
