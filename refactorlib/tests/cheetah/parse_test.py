
def test_can_make_round_trip():
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
		assert example == tostring(lxmlnode, method='text')
		print 'OK'

if __name__ == '__main__':
	exit(test_can_make_round_trip())
