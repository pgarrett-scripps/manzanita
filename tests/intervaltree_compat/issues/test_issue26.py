# Ported from intervaltree test/issues/issue26_test.py
"""
Test module: IntervalTree, insertion and removal of float intervals
Submitted as issue #26 (Pop from empty list error) by sciencectn
Ensure that rotations that promote Intervals prune when necessary

NOTE: test_minimal_sequence() is skipped because it accesses top_node internal.
"""
from manzanita import IntervalTree, Interval
import pytest


def test_original_sequence():
    t = IntervalTree()
    t.addi(17.89, 21.89)
    t.addi(11.53, 16.53)
    t.removei(11.53, 16.53)
    t.removei(17.89, 21.89)
    t.addi(-0.62, 4.38)
    t.addi(9.24, 14.24)
    t.addi(4.0, 9.0)
    t.removei(-0.62, 4.38)
    t.removei(9.24, 14.24)
    t.removei(4.0, 9.0)
    t.addi(12.86, 17.86)
    t.addi(16.65, 21.65)
    t.removei(12.86, 17.86)


def test_debug_sequence():
    t = IntervalTree()
    t.addi(17.89, 21.89)
    t.addi(11.53, 16.53)
    t.removei(11.53, 16.53)
    t.removei(17.89, 21.89)
    t.addi(-0.62, 4.38)
    t.addi(9.24, 14.24)
    t.addi(4.0, 9.0)
    t.removei(-0.62, 4.38)
    t.removei(9.24, 14.24)
    t.removei(4.0, 9.0)
    t.addi(12.86, 17.86)
    t.addi(16.65, 21.65)
    t.removei(12.86, 17.86)


# test_minimal_sequence() skipped -- accesses top_node internal


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
