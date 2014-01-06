#!/usr/bin/env python

from refactorlib.parse import parse

c = parse('simple.tmpl')

import pudb; pudb.set_trace()

for decorator in c.find_calls('foo'):
    print decorator.tostring()
    decorator.remove_self()

print c.totext()
