#!/usr/bin/env python
import setuptools

from refactorlib import __version__


setuptools.setup(
    name='refactorlib',
    version=__version__,
    author='Buck Golemon',
    author_email='buck@yelp.com',
    description='A library to help automate refactoring',
    long_description=open('README.markdown').read(),
    url='http://github.com/bukzor/RefactorLib/',
    packages=setuptools.find_packages(exclude=('tests*', 'testing*')),
    platforms='any',
    license='BSD',

    install_requires=[
        'cached-property',
        'lxml>=2.2',  # We run with 2.2.4.0
        'six',
    ],
    extras_require={
        'javascript': ['simplejson'],
        'cheetah': ['yelp_cheetah>=0.16.1,<=0.16.999'],
    },

    entry_points={
        'console_scripts': [
            'xmlfrom = refactorlib.cli.xmlfrom:cli',
            'xmlstrip = refactorlib.cli.xmlstrip:cli',
        ],
    },
    package_data={
        'refactorlib': [
            'javascript/reflectjs.js',
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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
