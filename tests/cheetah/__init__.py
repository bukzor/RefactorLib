import pytest

try:
    # pylint:disable=import-error
    import Cheetah
    del Cheetah
except ImportError:  # pragma: no cover
    xfailif_no_cheetah = pytest.mark.xfail(reason='cheetah not found')
else:
    xfailif_no_cheetah = pytest.mark.noop
