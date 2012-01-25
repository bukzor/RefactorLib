
def main():
	from refactorlib import TOP
	from os.path import join
	from os import listdir

	examples = join(TOP, 'tests/examples/cheetah')

	for example in listdir(examples):
		if not example.endswith('.tmpl'):
			continue

		example = open(join(examples, example)).read()

		from refactorlib.cheetah.parse import parse
		lxmlnode = parse(example)

		from lxml.etree import tostring
		print tostring(lxmlnode)
		assert example == tostring(lxmlnode, method='text')
		print 'OK'

if __name__ == '__main__':
	exit(main())
