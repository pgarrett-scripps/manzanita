# Ported from intervaltree test/intervaltree_methods/delete_test.py
"""
Test module: IntervalTree, Basic deletion methods
"""
from manzanita import Interval, IntervalTree
import pytest
from tests.intervaltree_compat import data
from tests.intervaltree_compat.conftest import set_data, make_tree_deduped


def test_delete():
    t = make_tree_deduped(data.ivs1.data)
    try:
        t.remove(Interval(1, 3, "Doesn't exist"))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")

    try:
        t.remove(Interval(500, 1000, "Doesn't exist"))
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")

    t.discard(Interval(1, 3, "Doesn't exist"))
    t.discard(Interval(500, 1000, "Doesn't exist"))

    assert set_data(t[14]) == set(['[8,15)', '[14,15)'])
    t.remove(Interval(14, 15, '[14,15)'))
    assert set_data(t[14]) == set(['[8,15)'])

    t.discard(Interval(8, 15, '[8,15)'))
    assert set_data(t[14]) == set()

    assert t[5]
    t.remove_overlap(5)
    assert not t[5]


def test_removei():
    # Empty tree
    e = IntervalTree()
    with pytest.raises(ValueError):
        e.removei(-1000, -999, "Doesn't exist")
    assert len(e) == 0

    # Non-existent member should raise ValueError
    t = make_tree_deduped(data.ivs1.data)
    oldlen = len(t)
    with pytest.raises(ValueError):
        t.removei(-1000, -999, "Doesn't exist")
    assert len(t) == oldlen

    # Should remove existing member
    assert Interval(1, 2, '[1,2)') in t
    t.removei(1, 2, '[1,2)')
    assert len(t) == oldlen - 1
    assert Interval(1, 2, '[1,2)') not in t


def test_discardi():
    # Empty tree
    e = IntervalTree()
    e.discardi(-1000, -999, "Doesn't exist")
    assert len(e) == 0

    # Non-existent member should do nothing quietly
    t = make_tree_deduped(data.ivs1.data)
    oldlen = len(t)
    t.discardi(-1000, -999, "Doesn't exist")
    assert len(t) == oldlen

    # Should discard existing member
    assert Interval(1, 2, '[1,2)') in t
    t.discardi(1, 2, '[1,2)')
    assert len(t) == oldlen - 1
    assert Interval(1, 2, '[1,2)') not in t


def test_emptying_iteration():
    t = make_tree_deduped(data.ivs1.data)

    for iv in sorted(list(t), key=lambda iv: (iv.begin, iv.end, str(iv.data))):
        t.remove(iv)
    assert len(t) == 0
    assert t.is_empty()
    assert not t


def test_emptying_clear():
    t = make_tree_deduped(data.ivs1.data)
    assert t
    t.clear()
    assert len(t) == 0
    assert t.is_empty()
    assert not t

    # make sure emptying an empty tree does not crash
    t.clear()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
