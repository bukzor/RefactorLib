#!/usr/bin/env python
from refactorlib import __version__

import setuptools
setuptools.setup(
    name = 'refactorlib',
    version = __version__,
    author = 'Buck Golemon',
    author_email = 'buck@yelp.com',
    description = 'A library to help automate refactoring',
    long_description = open('README.markdown').read(),
    url = 'http://github.com/bukzor/RefactorLib/',
    packages = ['refactorlib'],
	platforms = 'any',
    test_suite = 'refactorlib.tests',
    license = 'BSD',

    # See http://pypi.python.org/pypi?%3Aaction==list_classifiers
    classifiers = [
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
