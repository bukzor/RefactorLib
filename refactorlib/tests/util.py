"""
A home for the 'yellow code' of testing.
"""
def get_examples(typename, top=None):
	if top is None:
		from refactorlib import TOP as top
	from refactorlib.filetypes import FILETYPES
	from os.path import join
	from os import listdir

	filetype = FILETYPES.get_filetype(typename)

	examples = join(top, 'tests/%s/examples' % typename)

	for example in listdir(examples):
		if filetype.match(example):
			yield join(examples, example),

def get_output(modulefile, typename, suffix=None, top=None):
	from os.path import basename, join
	for example, in get_examples(typename, top=top):
		path = modulefile.rsplit('_test.py',1)[0] + '_output'
		fname = basename(example)
		if suffix:
			# Replace the suffix.
			fname = fname.rsplit('.',1)[0] + '.' + suffix
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
