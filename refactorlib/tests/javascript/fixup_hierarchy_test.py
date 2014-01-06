
def child(start, end, children=()):
    return {
            'start': start,
            'end': end,
            'children': list(children),
            'parent': None
    }
def set_children(parent, children):
    parent['children'] = children
    for child in children:
        child['parent'] = parent
    
from refactorlib.javascript.parse import fixup_hierarchy

class TestFixupHierarchy:
    def test_onechild(self):
        c1 = child(0, 1)
        c2 = child(0, 2)
        set_children(c1, [c2])
        result = fixup_hierarchy(c1)
        assert result is c1
        assert len(result['children']) == 1
        assert result['children'][0] is c2
        assert c1['end'] == c2['end'] == 1

    def test_fix_overlap(self):
        c1 = child(0, 6)
        c2 = child(2, 4)
        c3 = child(3, 5)
        set_children(c1, [c2, c3])
        result = fixup_hierarchy(c1)
        assert result['children'][0]['end'] == result['children'][1]['start'] == 3
        
    
    def test_widening(self):
        c0 = child(0, 10)
        c1 = child(0, 5)
        c2 = child(2, 4)
        c3 = child(2, 9)
        c4 = child(8, 9)
        set_children(c0, [c1])
        set_children(c1, [c2, c3])
        set_children(c3, [c4])

        fixup_hierarchy(c0)

        assert c0['children'][1] is c4
        assert (8, 9) == (c4['start'], c4['end'])
        assert c2['end'] == c3['start'] == 4
        assert c1['end'] == c3['end'] == 5


