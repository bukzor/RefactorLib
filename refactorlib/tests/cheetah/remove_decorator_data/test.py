#!/usr/bin/env python

from refactorlib.parse import parse

c = parse('foo.tmpl')

for decorator in c.find_decorators('foo'):
	print decorator.tostring()
	decorator.remove_self()

print c.totext()
