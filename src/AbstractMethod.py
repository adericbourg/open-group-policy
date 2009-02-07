# See http://code.activestate.com/recipes/266468/ for further details

class AbstractMethod (object):
	"""Defines a class to create abstract methods

	@example:
	class Foo:
	foo = AbstractMethod('foo')
	"""

	def __init__(self, func):
		"""Constructor

		@params func: name of the function (used when raising an
		exception).
		@type func: str
		"""
		self._function = func

	def __get__(self, obj, type):
		"""Get callable object

		@returns An instance of AbstractMethodHelper.

		This trickery is needed to get the name of the class for which
		an abstract method was requested, otherwise it would be
		sufficient to include a __call__ method in the AbstractMethod
		class itself.
		"""
		return self.AbstractMethodHelper(self._function, type)

class AbstractMethodHelper (object):
	"""Abstract method helper class

	An AbstractMethodHelper instance is a callable object that
	represents an abstract method.
	"""
	def __init__(self, func, cls):
		self._function = func
		self._class = cls

	def __call__(self, *args, **kwargs):
		"""Call abstract method

		Raises a TypeError, because abstract methods can not be
		called.
		"""
		raise TypeError('Abstract method `' + self._class.__name__ + '.' + self._function + '\' called')
