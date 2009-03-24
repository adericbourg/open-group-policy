#!/usr/bin/python
# -*- coding: utf-8 -*

def smart_bool(s):
	if s is True or s is False:
		return s
	else:
		s = str(s).strip().lower()
		return not s in ['false','f','n','0','']
