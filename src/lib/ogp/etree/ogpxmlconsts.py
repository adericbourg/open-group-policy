class M_OgpXmlConsts(type):
	def __setattr__(self, item, value):
		"""
			Plugin class and metaclass __setattr__ method
			Throws an exception when attempting to modify any class
			attribute.
		"""
		raise OgpPluginError('__setattr__: ' + item  + ' is readonly.')

class OgpXmlConsts:
	"""
		Provides XML tags and attributes names
	"""

	__metaclass__ = M_OgpXmlConsts

	ATTR_BLOCK = "block"
	ATTR_ID = "id"
	ATTR_PLUGIN_NAME = "name"
	ATTR_FILE_NAME = "name"
	TAG_OGP = "ogp"
	TAG_UID = "uid"
	TAG_GID = "gid"
	TAG_SECURITY = "security"
	TAG_FILE = "file"
	TAG_FILES = "files"
	TAG_PLUGIN = "plugin"

	TAGS_SECURITY = ['ux', 'ur', 'uw', 'us', 'gx', 'gr', 'gw', 'gs', 'ox', 'or', 'ow', 't']
