def cheetah_missing():
	"""returns False if Cheetah is not importable"""
	try:
		# F0401: can't import
		# pylint: disable=F0401
		import Cheetah
		del Cheetah
	except ImportError:
		return True
	else:
		return False

import pytest
pytestmark = pytest.mark.skipif(cheetah_missing(), reason='cheetah not found')
