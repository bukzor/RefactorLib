def test_can_find_and_remove_calls():
	from refactorlib.cheetah.parse import parse
	example = parse('''
		#def foo()
			x $foo() bar
		#end def
	''')

	calls = example.find_calls('foo')
	assert len(calls) == 1
	assert calls[0].totext() == '$foo()'

	calls[0].remove_call()

	assert example.totext() == '''
		#def foo()
			x  bar
		#end def
	'''

	
#TODO: this could use more exhoustive test cases
