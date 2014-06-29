#!/bin/env python
"""
A script to convert from any refactorlib-supported format to xml.
"""


def xmlfrom(filename):
    from refactorlib.parse import parse
    from lxml.etree import tostring

    tree = parse(filename).getroottree()
    encoding = tree.docinfo.encoding
    return tostring(tree, encoding=encoding)


def main(argv, stdout):
    # testability: this function should interact only with its arguments.
    # TODO: argparse. enable explicit filetype.
    stdout.write(xmlfrom(argv[1]))


def cli():
    # testability: this function should be trivial.
    from sys import argv, stdout
    return main(argv, stdout)


if __name__ == '__main__':
    # TODO: argparse. enable explicit filetype.
    exit(cli())
