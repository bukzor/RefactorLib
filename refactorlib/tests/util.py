def get_examples(typename):
	from refactorlib import TOP
	from refactorlib.filetypes import FILETYPES
	from os.path import join
	from os import listdir

	filetype = FILETYPES.get_filetype(typename)

	examples = join(TOP, 'tests/%s/examples' % typename)

	for example in listdir(examples):
		if filetype.match(example):
			yield(join(examples, example))

def get_output(modulefile, typename, suffix):
	from os.path import basename, join, exists
	for example in get_examples(typename):
		path = modulefile.rsplit('_test.py',1)[0] + '_output'
		fname = basename(example).rsplit('.',1)[0] + '.' + suffix
		output = join(path, fname)

		# print '%s -> %s ' % (example, output)
		if exists(output):
			yield example, output
