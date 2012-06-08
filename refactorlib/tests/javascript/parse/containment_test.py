
def child(startline, startcol, endline, endcol):
	return {
			'loc': {
				'start': {
					'line': startline,
					'column': startcol,
				},
				'end': {
					'line': endline,
					'column': endcol,
				},
			}
	}


from refactorlib.javascript.parse import resolve_containment
from py.test import raises

class TestContainment:
	def test_onechild(self):
		c1 = child(0, 0, 1, 1)
		c2 = child(0, 0, 0, 1)
		result = resolve_containment([c1, c2])
		assert len(result) == 1
		assert result[0] is c1
		assert len(result[0]['children']) == 1
		assert result[0]['children'][0] is c2

	def test_index_preserved(self):
		c1 = child(0, 0, 1, 1)
		c2 = child(0, 0, 0, 1)
		c3 = child(0, 0, 0, 1)
		result = resolve_containment([c3, c1, c2])
		assert result[0]['children'][0] is c3
		assert result[0]['children'][0]['children'][0] is c2
		result = resolve_containment([c1, c2, c3])
		assert result[0]['children'][0] is c2
		assert result[0]['children'][0]['children'][0] is c3
		
	def test_detect_overlap(self):
		c1 = child(0, 0, 1, 1)
		c2 = child(0, 2, 0, 4)
		c3 = child(0, 3, 0, 5)
		with raises(ValueError):
			resolve_containment([c3, c1, c2])
