# Ported from intervaltree test/issues/issue27_test.py
"""
Test module: IntervalTree, bracket notation vs overlap method equivalence
Submitted as issue #27
"""
from manzanita import IntervalTree, Interval
import pytest


def test_brackets_vs_overlap():
    it = IntervalTree()
    it.addi(1, 3, "dude")
    it.addi(2, 4, "sweet")
    it.addi(6, 9, "rad")
    for iobj in it:
        assert set(it[iobj.begin:iobj.end]) == set(it.overlap(iobj.begin, iobj.end))


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
