from refactorlib.tests.util import parametrize, get_output, assert_same_content

@parametrize(get_output('txt'))
def test_find_end_directive(example, output):
	text = open(example).read()

	from refactorlib.cheetah.parse import parse
	lxmlnode = parse(text)
	tree = lxmlnode.getroottree()

	new_output = []
	for directive in lxmlnode.xpath('//Directive'):
		new_output.append(
			'Directive: %s' % tree.getpath(directive),
		)
		if directive.is_multiline_directive:
			try:
				new_output.append(
					'End: %s' % tree.getpath(directive.get_end_directive()),
				)
			except:
				import pudb; pudb.set_trace()
				raise
		else:
			new_output.append(
				'Single-line: %s' % directive.totext()
			)
		new_output.append('')

	new_output = '\n'.join(new_output)
	assert_same_content(output, new_output)
