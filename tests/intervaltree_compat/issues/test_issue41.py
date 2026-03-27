# Ported from intervaltree test/issues/issue41_test.py
"""
Test module: IntervalTree, removal of intervals
Submitted as issue #41 (Interval removal breaks this tree) by escalonn

NOTE: test_structure() is skipped because it depends on internal Node class.
"""
from manzanita import IntervalTree
import pytest


def test_sequence():
    t = IntervalTree()
    t.addi(860, 917, 1)
    t.addi(860, 917, 2)
    t.addi(860, 917, 3)
    t.addi(860, 917, 4)
    t.addi(871, 917, 1)
    t.addi(871, 917, 2)
    t.addi(871, 917, 3)     # Value inserted here
    t.addi(961, 986, 1)
    t.addi(1047, 1064, 1)
    t.addi(1047, 1064, 2)
    t.removei(961, 986, 1)
    t.removei(871, 917, 3)  # Deleted here


# test_structure() skipped -- depends on internal Node class


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
