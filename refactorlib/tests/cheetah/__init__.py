def check_missing():
    """returns False if Cheetah is not importable"""
    try:
        # F0401: can't import
        # pylint: disable=F0401
        import Cheetah
        del Cheetah
    except ImportError:
        return pytest.mark.xfail(reason='cheetah not found')
    else:
        return pytest.mark.noop

import pytest
pytestmark = check_missing()
