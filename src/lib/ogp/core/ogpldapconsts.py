#!/usr/bin/python
# -*- coding: utf-8 -*

class OgpLDAPConsts:

	OBJECTCLASS_OU 			= "oGPOrganizationalUnit"
	OBJECTCLASS_MACHINE 	= "oGPComputer"

	ATTR_DESCRIPTION 		= "description"
	ATTR_CONFIG 			= "oGPXMLConfig"
	ATTR_SAMACCOUNTNAME		= "sAMAccountName"
	ATTR_OBJECTSID			= "objectSid"
	ATTR_OGPSOA				= "oGPSOA"
	ATTR_MACHINECERTIFICATE	= "oGPMachineCertificate"

	VALUE_CONFIG			= "<ogp/>"
	VALUE_SAMACCOUNTNAME	= "N/A"
	VALUE_OBJECTSID			= "\0"
	VALUE_OGPSOA			= "0"
