# For more informations, see http://code.activestate.com/recipes/266468/

class Metaclass (type):
	
	def __init__(cls, name, bases, *args, **kwargs):
		"""Configure a new class

		@param cls: Class object
		@param name: Name of the class
		@param bases: All base classes for cls
		"""
		super(Metaclass, cls).__init__(cls, name, bases, *args, **kwargs)

		# Detach cls.new() from class Metaclass, and make it a method
		# of cls.
		cls.__new__ = staticmethod(cls.new)

		# Find all abstract methods, and assign the resulting list to
		# cls.__abstractmethods__, so we can read that variable when a
		# request for allocation (__new__) is done.
		abstractmethods = []
		ancestors = list(cls.__mro__)
		ancestors.reverse()  # Start with __builtin__.object
		for ancestor in ancestors:
			for clsname, clst in ancestor.__dict__.items():
				if isinstance(clst, AbstractMethod):
					abstractmethods.append(clsname)
				else:
					if clsname in abstractmethods:
						abstractmethods.remove(clsname)

		abstractmethods.sort()
		setattr(cls, '__abstractmethods__', abstractmethods)

	def new(self, cls, *args, **kwargs):
		"""Allocator for class cls

		@param self: Class object for which an instance should be
			created.

		@param cls: Same as self.
		"""
		if len(cls.__abstractmethods__):
			raise NotImplementedError('Can\'t instantiate class `' + \
									  cls.__name__ + '\';\n' + \
									  'Abstract methods: ' + \
									  ", ".join(cls.__abstractmethods__))

		return object.__new__(self)
