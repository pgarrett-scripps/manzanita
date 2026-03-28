# Ported from intervaltree test/issues/issue72_test.py
"""
Test module: IntervalTree, remove_overlap caused incorrect balancing
where intervals overlapping an ancestor's x_center were buried too deep.
Submitted as issue #72 by alexandersoto
"""
from manzanita import IntervalTree, Interval
import pytest


def test_interval_removal_72():
    tree = IntervalTree([
        Interval(0.0, 2.588, 841),
        Interval(65.5, 85.8, 844),
        Interval(93.6, 130.0, 837),
        Interval(125.0, 196.5, 829),
        Interval(391.8, 521.0, 825),
        Interval(720.0, 726.0, 834),
        Interval(800.0, 1033.0, 850),
        Interval(800.0, 1033.0, 855),
    ])
    tree.remove_overlap(0.0, 521.0)
    # Should have removed 5 intervals (those overlapping 0-521)
    # Remaining: [720,726), [800,1033) x2
    assert len(tree) == 3


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
