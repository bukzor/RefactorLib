from refactorlib.cheetah.parse import parse

def test_can_find_calls():
	example = parse('''
		foo $foo() bar
	''')

	calls = example.find_calls('foo')
	assert len(calls) == 1
	assert calls[0].totext() == '$foo()'

def test_can_remove_calls():
	example = parse('''
		foo $foo() bar
		foo $foo(dotted.name) bar
		foo $foo($cheetahvar) bar
		foo $foo($cheetah.var) bar
		foo $foo(x.upper() for x in mylist) bar
	''')

	calls = example.find_calls('foo')
	assert len(calls) == 5

	for call in calls:
		call.remove_call()

	assert '''
		foo  bar
		foo $dotted.name bar
		foo $cheetahvar bar
		foo $cheetah.var bar
		foo $(x.upper() for x in mylist) bar
	''' == example.totext()

def test_can_remove_multiline_calls():
	example = parse('''
		foo $foo(
		) bar
		foo $foo(
			dotted.name
		) bar
		foo $foo(
			$cheetahvar
		) bar
		foo $foo(
			$cheetah.var
		) bar
		foo $foo(
			x.upper() for x in mylist
		) bar
	''')

	calls = example.find_calls('foo')
	assert len(calls) == 5

	for call in calls:
		call.remove_call()

	assert '''
		foo  bar
		foo $dotted.name bar
		foo $cheetahvar bar
		foo $cheetah.var bar
		foo $(
			x.upper() for x in mylist
		) bar
	''' == example.totext()

	
