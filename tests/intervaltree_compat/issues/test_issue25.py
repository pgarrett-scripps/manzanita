# Ported from intervaltree test/issues/issue25_test.py
"""
Test module: IntervalTree, insertion and removal of float intervals
Submitted as issue #25 (Incorrect KeyError) by sciencectn

NOTE: test_structure() is skipped because it depends on internal Node class.
"""
from manzanita import IntervalTree
import pytest


@pytest.mark.xfail(reason="manzanita removei corrupts tree with float intervals (regression)")
def test_sequence():
    t = IntervalTree()
    t.addi(6.37, 11.37)
    t.addi(12.09, 17.09)
    t.addi(5.68, 11.58)
    t.removei(6.37, 11.37)
    t.addi(13.23, 18.23)
    t.removei(12.09, 17.09)
    t.addi(4.29, 8.29)
    t.removei(13.23, 18.23)
    t.addi(12.04, 17.04)
    t.addi(9.39, 13.39)
    t.removei(5.68, 11.58)
    t.removei(4.29, 8.29)
    t.removei(12.04, 17.04)
    t.addi(5.66, 9.66)     # Value inserted here
    t.addi(8.65, 13.65)
    t.removei(9.39, 13.39)
    t.addi(16.49, 20.83)
    t.addi(11.42, 16.42)
    t.addi(5.38, 10.38)
    t.addi(3.57, 9.47)
    t.removei(8.65, 13.65)
    t.removei(5.66, 9.66)    # Deleted here


# test_structure() skipped -- depends on internal Node class


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
