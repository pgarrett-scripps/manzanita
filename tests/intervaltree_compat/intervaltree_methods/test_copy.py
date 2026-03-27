# Ported from intervaltree test/intervaltree_methods/copy_test.py
"""
Test module: IntervalTree, Copying
"""
from manzanita import Interval, IntervalTree
from tests.intervaltree_compat import data
from tests.intervaltree_compat.conftest import make_tree_deduped, sorted_iv


def test_copy():
    itree = IntervalTree([Interval(0, 1, "x"), Interval(1, 2, "y")])

    itree2 = IntervalTree(list(itree))  # Rebuild from intervals
    itree3 = itree.copy()

    assert sorted_iv(itree) == sorted_iv(itree2)
    assert sorted_iv(itree) == sorted_iv(itree3)


def test_copy_cast():
    t = make_tree_deduped(data.ivs1.data)

    tcopy = IntervalTree(list(t))
    assert t == tcopy

    tlist = list(t)
    for iv in tlist:
        assert iv in t
    for iv in t:
        assert iv in tlist

    tset = set(t)
    assert tset == set(t.items())


def test_copy_independence():
    """Test that copy is independent (modifying copy doesn't affect original)."""
    t = IntervalTree([Interval(0, 1, "x"), Interval(1, 2, "y")])
    c = t.copy()

    assert t == c
    c.add(Interval(5, 10, "z"))
    assert len(c) == 3
    assert len(t) == 2


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])
