__version__ = '0.0.0-dev'

if __file__[-1] in 'oc':
	# fixup for .pyc and .pyo files
	filename = __file__[:-1]
else:
	filename = __file__

from os.path import realpath, dirname
TOP = dirname(realpath(filename))

__all__ = ('TOP',)
