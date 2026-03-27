# Ported from intervaltree test/intervaltree_methods/restructure_test.py
"""
Test module: IntervalTree, Restructuring methods
"""
from manzanita import Interval, IntervalTree
import pytest
from tests.intervaltree_compat import data
from tests.intervaltree_compat.conftest import set_data, make_tree_deduped, sorted_iv


# -----------------------------------------------------------------------------
# REMOVAL
# -----------------------------------------------------------------------------
def test_emptying_partial():
    t = make_tree_deduped(data.ivs1.data)
    assert t[7:]
    t.remove_overlap(7, t.end())
    assert not t[7:]

    t = make_tree_deduped(data.ivs1.data)
    assert t[:7]
    t.remove_overlap(t.begin(), 7)
    assert not t[:7]


def test_remove_overlap():
    t = make_tree_deduped(data.ivs1.data)
    assert t[1]
    t.remove_overlap(1)
    assert not t[1]

    assert t[8]
    t.remove_overlap(8)
    assert not t[8]


# -----------------------------------------------------------------------------
# MERGE_OVERLAPS
# -----------------------------------------------------------------------------
def test_merge_overlaps_empty():
    t = IntervalTree()
    t.merge_overlaps()
    assert len(t) == 0


def test_merge_overlaps_gapless():
    # default strict=True
    t = make_tree_deduped(data.ivs2.data)
    t.merge_overlaps()
    assert [(iv.begin, iv.end, iv.data) for iv in sorted_iv(t)] == data.ivs2.data

    # strict=False
    t = make_tree_deduped(data.ivs2.data)
    t.merge_overlaps(strict=False)
    assert len(t) == 1


def test_merge_overlaps_with_gap():
    t = make_tree_deduped(data.ivs1.data)
    t.merge_overlaps()
    assert len(t) == 2
    ivs = sorted_iv(t)
    assert ivs[0] == Interval(1, 2, '[1,2)')
    assert ivs[1].begin == 4
    assert ivs[1].end == 15


# -----------------------------------------------------------------------------
# MERGE_EQUALS
# -----------------------------------------------------------------------------
def test_merge_equals_empty():
    t = IntervalTree()
    t.merge_equals()
    assert len(t) == 0


def test_merge_equals_wo_dupes():
    t = make_tree_deduped(data.ivs1.data)
    orig = make_tree_deduped(data.ivs1.data)
    assert t == orig

    t.merge_equals()
    assert orig == t


def test_merge_equals_with_dupes():
    t = make_tree_deduped(data.ivs1.data)
    orig = make_tree_deduped(data.ivs1.data)
    assert orig == t

    # one dupe
    assert t.containsi(4, 7, '[4,7)')
    t.addi(4, 7, 'foo')
    assert len(t) == len(orig) + 1
    assert orig != t

    t.merge_equals()
    assert t.containsi(4, 7)
    assert not t.containsi(4, 7, 'foo')
    assert not t.containsi(4, 7, '[4,7)')


# -----------------------------------------------------------------------------
# MERGE_NEIGHBORS
# -----------------------------------------------------------------------------
def test_merge_neighbors_empty():
    t = IntervalTree()
    t.merge_neighbors()
    assert len(t) == 0


def test_merge_neighbors_gapless():
    t = make_tree_deduped(data.ivs2.data)
    t.merge_neighbors()
    assert len(t) == 1
    for iv in t.items():
        assert iv.begin == data.ivs2.data[0][0]
        assert iv.end == data.ivs2.data[-1][1]


# -----------------------------------------------------------------------------
# CHOP
# -----------------------------------------------------------------------------
def test_chop():
    t = IntervalTree([Interval(0, 10)])
    t.chop(3, 7)
    assert len(t) == 2
    assert sorted_iv(t)[0] == Interval(0, 3)
    assert sorted_iv(t)[1] == Interval(7, 10)

    t = IntervalTree([Interval(0, 10)])
    t.chop(0, 7)
    assert len(t) == 1
    assert sorted_iv(t)[0] == Interval(7, 10)

    t = IntervalTree([Interval(0, 10)])
    t.chop(5, 10)
    assert len(t) == 1
    assert sorted_iv(t)[0] == Interval(0, 5)

    t = IntervalTree([Interval(0, 10)])
    t.chop(-5, 15)
    assert len(t) == 0

    t = IntervalTree([Interval(0, 10)])
    t.chop(0, 10)
    assert len(t) == 0


def test_chop_datafunc():
    def datafunc(iv, islower):
        # iv[int(islower)] returns float in manzanita, use int() for display
        oldlimit = iv[int(islower)]
        return "oldlimit: {0}, islower: {1}".format(oldlimit, islower)

    t = IntervalTree([Interval(0, 10)])
    t.chop(3, 7, datafunc)
    assert len(t) == 2
    # manzanita stores values as floats, so oldlimit will be e.g. 10.0
    assert sorted_iv(t)[0] == Interval(0, 3, 'oldlimit: 10.0, islower: True')
    assert sorted_iv(t)[1] == Interval(7, 10, 'oldlimit: 0.0, islower: False')

    t = IntervalTree([Interval(0, 10)])
    t.chop(0, 7, datafunc)
    assert len(t) == 1
    assert sorted_iv(t)[0] == Interval(7, 10, 'oldlimit: 0.0, islower: False')

    t = IntervalTree([Interval(0, 10)])
    t.chop(5, 10, datafunc)
    assert len(t) == 1
    assert sorted_iv(t)[0] == Interval(0, 5, 'oldlimit: 10.0, islower: True')

    t = IntervalTree([Interval(0, 10)])
    t.chop(-5, 15, datafunc)
    assert len(t) == 0

    t = IntervalTree([Interval(0, 10)])
    t.chop(0, 10, datafunc)
    assert len(t) == 0


# -----------------------------------------------------------------------------
# SLICE
# -----------------------------------------------------------------------------
def test_slice():
    t = IntervalTree([Interval(5, 15)])
    t.slice(10)
    assert sorted_iv(t)[0] == Interval(5, 10)
    assert sorted_iv(t)[1] == Interval(10, 15)

    t = IntervalTree([Interval(5, 15)])
    t.slice(5)
    assert sorted_iv(t)[0] == Interval(5, 15)

    t.slice(15)
    assert sorted_iv(t)[0] == Interval(5, 15)

    t.slice(0)
    assert sorted_iv(t)[0] == Interval(5, 15)

    t.slice(20)
    assert sorted_iv(t)[0] == Interval(5, 15)


def test_slice_datafunc():
    def datafunc(iv, islower):
        oldlimit = iv[int(islower)]
        return "oldlimit: {0}, islower: {1}".format(oldlimit, islower)

    t = IntervalTree([Interval(5, 15)])
    t.slice(10, datafunc)
    # manzanita stores values as floats
    assert sorted_iv(t)[0] == Interval(5, 10, 'oldlimit: 15.0, islower: True')
    assert sorted_iv(t)[1] == Interval(10, 15, 'oldlimit: 5.0, islower: False')

    t = IntervalTree([Interval(5, 15)])
    t.slice(5, datafunc)
    assert sorted_iv(t)[0] == Interval(5, 15)

    t.slice(15, datafunc)
    assert sorted_iv(t)[0] == Interval(5, 15)

    t.slice(0, datafunc)
    assert sorted_iv(t)[0] == Interval(5, 15)

    t.slice(20, datafunc)
    assert sorted_iv(t)[0] == Interval(5, 15)


# -----------------------------------------------------------------------------
# SPLIT
# -----------------------------------------------------------------------------
def test_split_overlap_empty():
    t = IntervalTree()
    t.split_overlaps()
    assert not t


def test_split_overlap_single_member():
    t = IntervalTree([Interval(0, 1)])
    t.split_overlaps()
    assert len(t) == 1


def test_split_overlap():
    t = make_tree_deduped(data.ivs1.data)

    t.split_overlaps()

    while t:
        iv = list(t)[0]
        t.remove(iv)
        for other in t.overlap(iv.begin, iv.end):
            assert other.begin == iv.begin
            assert other.end == iv.end


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
