#!/usr/bin/python
# -*- coding: utf-8 -*
from lxml.etree import *
from DomElementMethods import *

obj = Element("rootelement")
obj2 = Element("rootelement")

print "------ BLOCKING ------"
print obj.toString()
obj.blocking = True
print obj.toString()
obj.blocking = False
print obj.toString()
print "------- ADD --------"
elt = Element("inserted")
elt2 = Element("inserted")
obj.append(elt)
try:
	obj.append(elt2)
except OgpXmlError:
	print "crash"

print obj.toString()

print "------ DEL -------"
print obj.toString()
obj.delElements()
print obj.toString()

print "------ EXTEND -------"
print obj.toString()
try:
	obj.extend([elt, elt2])
except:
	print "crash"
print obj.toString()
obj.delElements()
elt3 = Element("pouet3")
obj.extend([elt, elt3])
print obj.toString()

print "--------- MERGE ----------"
print (obj.text is None)
print (obj2.text is None)
obj.delElements()
obj2.delElements()
obj.append(elt)
obj2.append(elt3)
print obj.toString()
print obj2.toString()
obj2.merge(obj)
print tostring(obj2)

print "   Avec du texte maintenant"
obj3 = Element("AAA")
obj4 = Element("AAA")
obj3.text = "pouet"
obj4.text = "I'm not dead"
print tostring(obj3)
print tostring(obj4)
obj4.merge(obj3)
print tostring(obj3)
print tostring(obj4)

print " -------SETTEXT----------"
obj.delElements()
obj.append(elt)
print obj.toString()
obj.text = "toto"
print obj.text
print obj.toString()

print "------- TOSTRING -----------"

