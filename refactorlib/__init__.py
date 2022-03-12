__version__ = '0.15.0'


def module_dir(modulefile):
    if modulefile[-1] in 'oc':
        # fixup for .pyc and .pyo files
        filename = modulefile[:-1]
    else:
        filename = modulefile

    from os.path import realpath, dirname
    return dirname(realpath(filename))


TOP = module_dir(__file__)
__all__ = ('__version__', 'module_dir', 'TOP')
