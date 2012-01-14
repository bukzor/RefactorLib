
def main():
	from refactorlib import TOP
	from os.path import join
	from os import listdir

	examples = join(TOP, 'tests/examples/python')

	for example in listdir(examples):
		if not example.endswith('.py'):
			continue

		example = open(join(examples, example)).read()

		from refactorlib.python.parse import parse
		lxmlnode = parse(example)

		from lxml.etree import tostring
		assert example == tostring(lxmlnode, method='text')
		print 'OK'

if __name__ == '__main__':
	exit(main())
