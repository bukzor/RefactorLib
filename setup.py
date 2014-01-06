#!/usr/bin/env python

def main():
    from refactorlib import __version__
    import setuptools
    setuptools.setup(
        name='refactorlib',
        version=__version__,
        author='Buck Golemon',
        author_email='buck@yelp.com',
        description='A library to help automate refactoring',
        long_description=open('README.markdown').read(),
        url='http://github.com/bukzor/RefactorLib/',
        packages=setuptools.find_packages('.'),
        platforms='any',
        cmdclass={'test': PyTest},
        license='BSD',

        install_requires=['lxml>=2.2'], # We run with 2.2.4.0

        scripts=['xmlfrom', 'xmlstrip'],

        # See http://pypi.python.org/pypi?%3Aaction==list_classifiers
        classifiers=[
            'Development Status :: 1 - Planning',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            #'Programming Language :: Python :: 2.4',
            #'Programming Language :: Python :: 2.5',
            'Programming Language :: Python :: 2.6',
            #'Programming Language :: Python :: 2.7',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )

from setuptools.command.test import test
class PyTest(test):
    """
    Hook up py.test to `setup.py test`
    see: http://pytest.org/latest/goodpractises.html
    """
    def get_pytest(self):
        try:
            import pytest
            return pytest
        except ImportError:
            from os import environ
            if 'VIRTUAL_ENV' in environ:
                # We run with 2.2.1
                import subprocess
                errno = subprocess.call(['pip', 'install', 'pytest>=2.2'])
                if errno: raise SystemExit(errno)
                import pytest
                return pytest
            else:
                raise

    def run(self):
        pytest = self.get_pytest()

        # remove commandline args so that pytest doesn't get confused
        from sys import argv
        del argv[:]

        print 'Run `py.test` for more control over testing.'
        raise SystemExit(pytest.cmdline.main())

if __name__ == '__main__':
    main()
