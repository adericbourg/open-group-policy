#!/usr/bin/python
# -*- coding: utf-8 -*

from ogp.core import *

uri = "ldap://localhost:389"
dn = "cn=admin,dc=nodomain"
passwd = "toor"

# Connection
ogp = OgpCore(uri, dn, passwd)

# Create OU
#ogp.createOU("ou=titi322,ou=tutu,dc=ogp","Bonjour, je teste en direct")
#ogp.createMachine('cn=la,ou=titi322,ou=tutu,dc=ogp')

#toto = "<file>Ceci est un test</file>"

#ogp.push(toto, 'cn=mac2,ou=titi,ou=tutu,dc=ogp')

#ogp.deleteOU("cn=la,ou=titi322,ou=tutu,dc=ogp")

toto = OgpCore.getInstance()

#toto.createOU("ou=test2,ou=test,dc=nodomain")
print toto.pullPluginConf("ou=test2,ou=test,dc=nodomain", "test", True).toString()
