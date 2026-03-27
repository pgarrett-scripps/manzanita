# Ported from intervaltree test/intervaltree_methods/insert_test.py
"""
Test module: IntervalTree, Basic insertion methods
"""
from manzanita import Interval, IntervalTree
import pytest
from tests.intervaltree_compat import data
from tests.intervaltree_compat.conftest import set_data, make_tree_deduped


def test_insert():
    tree = IntervalTree()

    tree[0:1] = "data"
    assert len(tree) == 1
    assert set(tree.items()) == set([Interval(0, 1, "data")])

    tree.add(Interval(10, 20))
    assert len(tree) == 2
    assert set(tree.items()) == set([Interval(0, 1, "data"), Interval(10, 20)])

    tree.addi(19.9, 20)
    assert len(tree) == 3
    assert set(tree.items()) == set([
        Interval(0, 1, "data"),
        Interval(19.9, 20),
        Interval(10, 20),
    ])

    tree.update([Interval(19.9, 20.1), Interval(20.1, 30)])
    assert len(tree) == 5
    assert set(tree.items()) == set([
        Interval(0, 1, "data"),
        Interval(19.9, 20),
        Interval(10, 20),
        Interval(19.9, 20.1),
        Interval(20.1, 30),
    ])


def test_duplicate_insert():
    tree = IntervalTree()

    # string data
    tree[-10:20] = "arbitrary data"
    contents = frozenset([Interval(-10, 20, "arbitrary data")])

    assert len(tree) == 1
    assert set(tree.items()) == contents

    # NOTE: manzanita allows duplicates, unlike intervaltree.
    # intervaltree would keep len==1 here, manzanita may not.
    # We test that at least 1 copy exists.
    tree.addi(-10, 20, "arbitrary data")
    assert Interval(-10, 20, "arbitrary data") in tree


def test_same_range_insert():
    t = make_tree_deduped(data.ivs1.data)

    t.add(Interval(14, 15, '[14,15)####'))
    assert set_data(t[14]) == set(['[8,15)', '[14,15)', '[14,15)####'])


def test_add_invalid_interval():
    """
    Ensure that begin < end.
    """
    itree = IntervalTree()
    with pytest.raises(ValueError):
        itree.addi(1, 0)

    with pytest.raises(ValueError):
        itree.addi(1, 1)

    with pytest.raises(ValueError):
        itree[1:0] = "value"

    with pytest.raises(ValueError):
        itree[1:1] = "value"

    with pytest.raises(ValueError):
        itree[1.1:1.05] = "value"

    with pytest.raises(ValueError):
        itree[1.1:1.1] = "value"


def test_insert_to_filled_tree():
    t = make_tree_deduped(data.ivs1.data)

    assert set_data(t[1]) == set(['[1,2)'])
    t.add(Interval(1, 2, '[1,2)'))  # adding duplicate
    # manzanita allows duplicates, so we just check data is still present
    assert '[1,2)' in set_data(t[1])

    assert Interval(2, 4, '[2,4)') not in t
    t.add(Interval(2, 4, '[2,4)'))
    assert set_data(t[2]) == set(['[2,4)'])

    t[13:15] = '[13,15)'
    assert set_data(t[14]) >= set(['[8,15)', '[13,15)', '[14,15)'])


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
