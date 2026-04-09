# Ported from intervaltree test/intervaltree_methods/setlike_test.py
"""
Test module: IntervalTree, Set-like operations
"""
from manzanita import Interval, IntervalTree
import pytest
from tests.intervaltree_compat import data
from tests.intervaltree_compat.conftest import make_tree_deduped, sorted_iv


def test_update():
    t = IntervalTree()
    interval = Interval(0, 1)
    s = [interval]

    t.update(s)
    assert isinstance(t, IntervalTree)
    assert len(t) == 1
    assert list(t)[0] == interval

    interval = Interval(2, 3)
    t.update([interval])
    assert isinstance(t, IntervalTree)
    assert len(t) == 2
    assert sorted_iv(t)[1] == interval


def test_union():
    t = IntervalTree()
    interval = Interval(0, 1)
    s = [interval]

    # union with empty
    r = t.union(IntervalTree(s))
    assert len(r) == 1
    assert list(r)[0] == interval

    # commutativity with full overlaps, then no overlaps
    a = make_tree_deduped(data.ivs1.data)
    b = make_tree_deduped(data.ivs2.data)
    e = IntervalTree()

    aa = a.union(a)
    ae = a.union(e)
    ea = e.union(a)
    ee = e.union(e)
    assert aa == a
    assert ae == a
    assert ea == a
    assert ee == e

    ab = a.union(b)
    ba = b.union(a)
    assert ab == ba

    # commutativity with strict subset overlap
    aba = ab.union(a)
    abb = ab.union(b)
    bab = ba.union(b)
    baa = ba.union(a)
    assert aba == abb
    assert abb == bab
    assert bab == baa
    assert aba == ab

    # commutativity with partial overlap
    c = make_tree_deduped(data.ivs3.data)
    bc = b.union(c)
    cb = c.union(b)
    assert bc == cb
    assert len(bc) > len(b)
    assert len(bc) > len(c)
    assert len(bc) < len(b) + len(c)
    for iv in b:
        assert iv in bc
    for iv in c:
        assert iv in bc


def test_union_operator():
    t = IntervalTree()
    interval = Interval(0, 1)
    s = [interval]

    r = t | IntervalTree(s)
    assert len(r) == 1
    assert sorted_iv(r)[0] == interval

    t |= IntervalTree(s)
    assert len(t) == 1
    assert sorted_iv(t)[0] == interval


def test_difference():
    minuend = make_tree_deduped(data.ivs1.data)
    assert isinstance(minuend, IntervalTree)
    subtrahend = minuend.copy()
    expected_difference = IntervalTree([subtrahend.pop()])
    expected_difference.add(subtrahend.pop())

    assert len(expected_difference) == len(minuend) - len(subtrahend)

    for iv in expected_difference:
        assert iv not in subtrahend
        assert iv in minuend

    difference = minuend.difference(subtrahend)

    for iv in difference:
        assert iv not in subtrahend
        assert iv in minuend
        assert iv in expected_difference

    assert difference == expected_difference


def test_difference_operator():
    minuend = make_tree_deduped(data.ivs1.data)
    assert isinstance(minuend, IntervalTree)
    subtrahend = minuend.copy()
    expected_difference = IntervalTree([subtrahend.pop()])
    expected_difference.add(subtrahend.pop())

    assert len(expected_difference) == len(minuend) - len(subtrahend)

    for iv in expected_difference:
        assert iv not in subtrahend
        assert iv in minuend

    difference = minuend - subtrahend

    for iv in difference:
        assert iv not in subtrahend
        assert iv in minuend
        assert iv in expected_difference

    assert difference == expected_difference


def test_intersection():
    a = make_tree_deduped(data.ivs1.data)
    b = make_tree_deduped(data.ivs2.data)
    e = IntervalTree()

    # intersections with e
    assert a.intersection(e) == e
    ae = a.copy()
    ae.intersection_update(e)
    assert ae == e

    assert b.intersection(e) == e
    be = b.copy()
    be.intersection_update(e)
    assert be == e

    assert e.intersection(e) == e
    ee = e.copy()
    ee.intersection_update(e)
    assert ee == e

    # intersections with self
    assert a.intersection(a) == a
    aa = a.copy()
    aa.intersection_update(a)
    assert aa == a

    assert b.intersection(b) == b
    bb = b.copy()
    bb.intersection_update(b)
    assert bb == b

    # commutativity resulting in empty
    ab = a.intersection(b)
    ba = b.intersection(a)
    assert ab == ba
    assert len(ab) == 0  # no overlaps, so empty tree

    ab = a.copy()
    ab.intersection_update(b)
    ba = b.copy()
    ba.intersection_update(a)
    assert ab == ba
    assert len(ab) == 0

    # commutativity on non-overlapping sets
    ab = a.union(b)
    ba = b.union(a)
    aba = ab.intersection(a)
    abb = ab.intersection(b)
    bab = ba.intersection(b)
    baa = ba.intersection(a)
    assert aba == a
    assert abb == b
    assert bab == b
    assert baa == a

    ab = a.union(b)
    ba = b.union(a)
    aba = ab.copy()
    aba.intersection_update(a)
    abb = ab.copy()
    abb.intersection_update(b)
    bab = ba.copy()
    bab.intersection_update(b)
    baa = ba.copy()
    baa.intersection_update(a)
    assert aba == a
    assert abb == b
    assert bab == b
    assert baa == a

    # commutativity with overlapping sets
    c = make_tree_deduped(data.ivs3.data)
    bc = b.intersection(c)
    cb = c.intersection(b)
    assert bc == cb
    assert len(bc) < len(b)
    assert len(bc) < len(c)
    assert len(bc) > 0
    assert b.containsi(13, 23)
    assert c.containsi(13, 23)
    assert bc.containsi(13, 23)
    assert not b.containsi(819, 828)
    assert not c.containsi(0, 1)
    assert not bc.containsi(819, 828)
    assert not bc.containsi(0, 1)

    bc = b.copy()
    bc.intersection_update(c)
    cb = c.copy()
    cb.intersection_update(b)
    assert bc == cb
    assert len(bc) < len(b)
    assert len(bc) < len(c)
    assert len(bc) > 0


def test_symmetric_difference():
    a = make_tree_deduped(data.ivs1.data)
    b = make_tree_deduped(data.ivs2.data)
    e = IntervalTree()

    # symdiffs with e
    assert a.symmetric_difference(e) == a
    ae = a.copy()
    ae.symmetric_difference_update(e)
    assert ae == a

    assert b.symmetric_difference(e) == b
    be = b.copy()
    be.symmetric_difference_update(e)
    assert be == b

    assert e.symmetric_difference(e) == e
    ee = e.copy()
    ee.symmetric_difference_update(e)
    assert ee == e

    # symdiff with self
    assert a.symmetric_difference(a) == e
    aa = a.copy()
    aa.symmetric_difference_update(a)
    assert aa == e

    assert b.symmetric_difference(b) == e
    bb = b.copy()
    bb.symmetric_difference_update(b)
    assert bb == e

    # commutativity resulting in sum (no overlaps)
    ab = a.symmetric_difference(b)
    ba = b.symmetric_difference(a)
    assert ab == ba
    assert len(ab) == len(a) + len(b)

    ab = a.copy()
    ab.symmetric_difference_update(b)
    ba = b.copy()
    ba.symmetric_difference_update(a)
    assert ab == ba
    assert len(ab) == len(a) + len(b)

    # commutativity on non-overlapping sets
    ab = a.union(b)
    ba = b.union(a)
    aba = ab.symmetric_difference(a)
    abb = ab.symmetric_difference(b)
    bab = ba.symmetric_difference(b)
    baa = ba.symmetric_difference(a)
    assert aba == b
    assert abb == a
    assert bab == a
    assert baa == b

    ab = a.union(b)
    ba = b.union(a)
    aba = ab.copy()
    aba.symmetric_difference_update(a)
    abb = ab.copy()
    abb.symmetric_difference_update(b)
    bab = ba.copy()
    bab.symmetric_difference_update(b)
    baa = ba.copy()
    baa.symmetric_difference_update(a)
    assert aba == b
    assert abb == a
    assert bab == a
    assert baa == b

    # commutativity with overlapping sets
    c = make_tree_deduped(data.ivs3.data)
    bc = b.symmetric_difference(c)
    cb = c.symmetric_difference(b)
    assert bc == cb
    assert len(bc) > 0
    assert len(bc) < len(b) + len(c)
    assert b.containsi(13, 23)
    assert c.containsi(13, 23)
    assert not bc.containsi(13, 23)
    assert c.containsi(819, 828)
    assert not b.containsi(819, 828)
    assert b.containsi(0, 1)
    assert not c.containsi(0, 1)
    assert bc.containsi(819, 828)
    assert bc.containsi(0, 1)

    bc = b.copy()
    bc.symmetric_difference_update(c)
    cb = c.copy()
    cb.symmetric_difference_update(b)
    assert bc == cb


def test_invalid_update():
    """In manzanita, invalid intervals raise ValueError at construction time."""
    with pytest.raises(ValueError):
        Interval(1, 0)  # begin > end

    with pytest.raises(ValueError):
        Interval(1, 1)  # begin == end


def test_invalid_union():
    """In manzanita, invalid intervals raise ValueError at construction time."""
    with pytest.raises(ValueError):
        Interval(1, 0)  # begin > end


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
