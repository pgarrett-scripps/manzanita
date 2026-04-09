# Ported from intervaltree test/interval_methods/binary_test.py
"""
Test module: Intervals, methods on two intervals
"""
from manzanita import Interval
import pytest

iv0 = Interval(0, 10)
iv1 = Interval(-10, -5)
iv2 = Interval(-10, 0)
iv3 = Interval(-10, 5)
iv4 = Interval(-10, 10)
iv5 = Interval(-10, 20)
iv6 = Interval(0, 20)
iv7 = Interval(5, 20)
iv8 = Interval(10, 20)
iv9 = Interval(15, 20)
iv10 = Interval(-5, 0)


def test_interval_overlaps_size_interval():
    assert iv0.overlap_size(iv0.begin, iv0.end) == 10
    assert iv0.overlap_size(iv1.begin, iv1.end) == 0
    assert iv0.overlap_size(iv2.begin, iv2.end) == 0
    assert iv0.overlap_size(iv3.begin, iv3.end) == 5
    assert iv0.overlap_size(iv4.begin, iv4.end) == 10
    assert iv0.overlap_size(iv5.begin, iv5.end) == 10
    assert iv0.overlap_size(iv6.begin, iv6.end) == 10
    assert iv0.overlap_size(iv7.begin, iv7.end) == 5
    assert iv0.overlap_size(iv8.begin, iv8.end) == 0
    assert iv0.overlap_size(iv9.begin, iv9.end) == 0


def test_interval_overlap_interval():
    assert iv0.overlaps_interval(iv0)
    assert not iv0.overlaps_interval(iv1)
    assert not iv0.overlaps_interval(iv2)
    assert iv0.overlaps_interval(iv3)
    assert iv0.overlaps_interval(iv4)
    assert iv0.overlaps_interval(iv5)
    assert iv0.overlaps_interval(iv6)
    assert iv0.overlaps_interval(iv7)
    assert not iv0.overlaps_interval(iv8)
    assert not iv0.overlaps_interval(iv9)


def test_contains_interval():
    assert iv0.contains_interval(iv0)
    assert not iv0.contains_interval(iv1)
    assert not iv0.contains_interval(iv2)
    assert not iv0.contains_interval(iv3)
    assert not iv0.contains_interval(iv4)
    assert not iv0.contains_interval(iv5)
    assert not iv0.contains_interval(iv6)
    assert not iv0.contains_interval(iv7)
    assert not iv0.contains_interval(iv8)
    assert not iv0.contains_interval(iv9)
    assert not iv0.contains_interval(iv10)

    # iv2 = Interval(-10, 0) contains iv1 = Interval(-10, -5) and iv10 = Interval(-5, 0)
    assert not iv2.contains_interval(iv0)
    assert iv2.contains_interval(iv1)
    assert iv2.contains_interval(iv2)
    assert not iv2.contains_interval(iv3)
    assert not iv2.contains_interval(iv4)
    assert not iv2.contains_interval(iv5)
    assert not iv2.contains_interval(iv6)
    assert not iv2.contains_interval(iv7)
    assert not iv2.contains_interval(iv8)
    assert not iv2.contains_interval(iv9)
    assert iv2.contains_interval(iv10)


def test_distance_to_interval():
    assert iv0.distance_to(iv0) == 0
    assert iv0.distance_to(iv1) == 5
    assert iv0.distance_to(iv2) == 0
    assert iv0.distance_to(iv3) == 0
    assert iv0.distance_to(iv4) == 0
    assert iv0.distance_to(iv5) == 0
    assert iv0.distance_to(iv6) == 0
    assert iv0.distance_to(iv7) == 0
    assert iv0.distance_to(iv8) == 0
    assert iv0.distance_to(iv9) == 5
    assert iv0.distance_to(iv10) == 0


def test_distance_to_point():
    assert iv0.distance_to(-5.0) == 5
    assert iv0.distance_to(0.0) == 0
    assert iv0.distance_to(5.0) == 0
    assert iv0.distance_to(10.0) == 0
    assert iv0.distance_to(15.0) == 5


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
