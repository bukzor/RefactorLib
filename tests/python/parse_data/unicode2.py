# vim:fileencoding=cp1251:

# See: http://www.cl.cam.ac.uk/~mgk25/ucs/examples/quickbrown.txt

# These should be entirely equivalent:
print u'''
В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!
(= Would a citrus live in the bushes of south? Yes, but only a fake one!)

Съешь же ещё этих мягких французских булок да выпей чаю
(= Eat some more of these fresh French loafs and have some tea) 
'''

print '''
В чащах юга жил бы цитрус? Да, но фальшивый экземпляр!
(= Would a citrus live in the bushes of south? Yes, but only a fake one!)

Съешь же ещё этих мягких французских булок да выпей чаю
(= Eat some more of these fresh French loafs and have some tea) 
'''.decode('cp1251')
