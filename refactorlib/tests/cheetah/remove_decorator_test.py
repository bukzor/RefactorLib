from refactorlib.tests.util import parametrize, get_output, assert_same_content

@parametrize(get_output)
def test_remove_foo(example, output):
	from refactorlib.cheetah.parse import parse
	example = open(example).read()
	example = parse(example)

	for decorator in example.find_decorators('foo'):
		print 'DECORATOR', decorator.tostring()
		decorator.remove_self()

	# Check the text.
	example = example.totext()
	assert_same_content(output, example)

