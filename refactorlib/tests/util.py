"""
A home for the 'yellow code' of testing.
"""
from os.path import join

def example_dir(func):
	from os.path import relpath

	modulefile = __import__(func.__module__, fromlist=True).__file__
	dirname = modulefile.rsplit('_test',1)[0] + '_data'
	return relpath(dirname)

def get_examples(func):

	from os import listdir
	from os.path import isfile

	examples = example_dir(func)
	examples_found = False

	for example in listdir(examples):
		if example.startswith('.'):
			# Hidden file.
			continue

		example = join(examples, example)
		if isfile(example):
			yield example,
			examples_found = True
	
	if not examples_found:
		raise SystemError("No examples found in %r" % examples)

def get_output(suffix=None):
	def _get_output(func):
		from os.path import split
		for example, in get_examples(func):

			dirname, filename = split(example)
			output = join(dirname, func.__name__, filename)
			if suffix: # Replace the suffix.
				output = output.rsplit('.',1)[0] + '.' + suffix

			yield example, output

	# The silly optionally-called decorator pattern.
	if callable(suffix):
		func, suffix = suffix, None
		return _get_output(func)
	else:
		return _get_output

def parametrize(arg_finder):
	def decorator(func):
		arglist = arg_finder(func)
		arglist = tuple(arglist) # freeze any generators

		from py.test import mark
		from inspect import getargspec
		return mark.parametrize(getargspec(func).args, arglist)(func)
	return decorator

def output_suffix(suffix):
	def decorator(func):
		func.output_suffix = suffix
		return func
	return decorator

def assert_same_content(old_file, new_content):
	new_file = old_file+'.test_failure'
	try:
		open(new_file,'w').write(new_content)
	except IOError, e:
		if e.errno == 2: # No such file.
			from os import makedirs
			from os.path import dirname
			makedirs(dirname(new_file))
			open(new_file,'w').write(new_content)
		else:
			raise

	assert_same_file_content(old_file, new_file)


def assert_same_file_content(old_file, new_file):
	old_content = open(old_file).readlines()
	new_content = open(new_file).readlines()

	from difflib import ndiff as diff
	diffs = '\n'.join(
			line.rstrip('\n')
			for line in diff(old_content, new_content)
			if not line.startswith('  ') # Remove the similar lines.
	)

	if diffs:
		diffs = 'Results differ:\n--- %s\n+++ %s\n%s' % (old_file, new_file, diffs)
		raise AssertionError(diffs)
	else:
		from os import unlink
		unlink(new_file)

