#!/usr/bin/python
# -*- coding: utf-8 -*

from lxml.etree import *
from ogp import etree
from ogp.core import *
core = OgpCore('ldap://localhost', 'cn=mac1,dc=nodomain', 'toto')

schema_f = open('ogpxmlconfig.xsd')
schema = etree.XMLSchema(parse(schema_f))

tree=fromstring('<ogp><plugin name="motd"><conf><distro>debian</distro></conf><files><file name="motd"><conf>caca!</conf><security/></file><file name="motd.tail"><conf/><security/></file></files></plugin></ogp>', OGP_PARSER)

print schema.validate(tree)
