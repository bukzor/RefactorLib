#!/bin/env python
"""
A script to convert from xml to text.
This is the inverse operation of `xmlfrom`.
"""


def xmlstrip(filename):
    from lxml.etree import XML, tostring
    tree = XML(open(filename, 'rb').read()).getroottree()
    encoding = tree.docinfo.encoding
    return tostring(tree, method='text', encoding=encoding)


def main(argv, stdout):
    # testability: this function should interact only with its arguments.
    # TODO: argparse. enable explicit filetype.
    stdout.write(xmlstrip(argv[1]))


def cli():
    # testability: this function should be trivial.
    from sys import argv, stdout
    return main(argv, stdout)


if __name__ == '__main__':
    exit(cli())
