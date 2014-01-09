#!/usr/bin/env python
"""The installer script."""

def main():
    """Our entry point."""
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

        tests_require=['pytest'],
        install_requires=['lxml>=2.2'], # We run with 2.2.4.0
        extras_require={
            'javascript': ['simplejson'],
            'cheetah': ['cheetah'],
            # Things I personally use to develop this package.
            'dev': ['pudb', 'pylint'],
        },

        entry_points={
                'console_scripts': [
                    'xmlfrom = refactorlib.cli.xmlfrom:cli',
                    'xmlstrip = refactorlib.cli.xmlstrip:cli',
                ],
        },

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


from setuptools.command.test import test as TestCommand
class PyTest(TestCommand):
    """
    Integrate `setup.py test` with py.test
    Stolen directly from the docs:
     http://pytest.org/latest/goodpractises.html#integration-with-setuptools-test-commands
    """
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        exit(errno)


if __name__ == '__main__':
    main()
