
def test_can_make_round_trip():
	from refactorlib import TOP
	from os.path import join
	from os import listdir

	examples = join(TOP, 'tests/cheetah/examples')

	for example in listdir(examples):
		if not example.endswith('.tmpl'):
			continue

		example = open(join(examples, example)).read()

		from refactorlib.cheetah.parse import parse
		lxmlnode = parse(example)

		from lxml.etree import tostring
		assert example == tostring(lxmlnode, method='text')
		print 'OK'


def test_matches_known_good_parsing():
	from refactorlib import TOP
	from os.path import join
	from os import listdir

	example_path = join(TOP, 'tests/cheetah/examples')
	xml_path = join(TOP, 'tests/cheetah/parse_output')

	for example in listdir(example_path):
		if not example.endswith('.tmpl'):
			continue

		xml = open(join(xml_path, example[:-4] + 'xml')).read()
		example = open(join(example_path, example)).read()

		from refactorlib.cheetah.parse import parse
		lxmlnode = parse(example)

		from lxml.etree import tostring
		assert xml == tostring(lxmlnode)
