"""
A home for the 'yellow code' of testing.
"""
def get_examples(typename):
	from refactorlib import TOP
	from refactorlib.filetypes import FILETYPES
	from os.path import join
	from os import listdir

	filetype = FILETYPES.get_filetype(typename)

	examples = join(TOP, 'tests/%s/examples' % typename)

	for example in listdir(examples):
		if filetype.match(example):
			yield join(examples, example),

def get_output(modulefile, typename, suffix):
	from os.path import basename, join
	for example, in get_examples(typename):
		path = modulefile.rsplit('_test.py',1)[0] + '_output'
		fname = basename(example).rsplit('.',1)[0] + '.' + suffix
		output = join(path, fname)

		yield example, output

def parametrize(arglist):
	arglist = tuple(arglist) # freeze any generators
	def decorator(func):
		from py.test import mark
		from inspect import getargspec
		return mark.parametrize(getargspec(func).args, arglist)(func)
	return decorator

def output_suffix(suffix):
	def decorator(func):
		func.output_suffix = suffix
		return func
	return decorator
