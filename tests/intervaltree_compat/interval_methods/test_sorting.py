# Ported from intervaltree test/interval_methods/sorting_test.py
"""
Test module: Intervals, sorting and overlap methods

NOTE: gt(), ge(), lt(), le(), __cmp__() are not available in manzanita.
      overlaps() with Interval arg is mapped to overlaps_interval().
      overlaps() with two numeric args is mapped to overlaps_range().
"""
from manzanita import Interval
import pytest


def test_interval_overlaps_point():
    iv = Interval(0, 10)

    assert not iv.overlaps(-5)
    assert iv.overlaps(0)
    assert iv.overlaps(5)
    assert not iv.overlaps(10)
    assert not iv.overlaps(15)


def test_interval_overlaps_range():
    iv0 = Interval(0, 10)

    assert not iv0.overlaps_range(-10, -5)
    assert not iv0.overlaps_range(-10, 0)
    assert iv0.overlaps_range(-10, 5)
    assert iv0.overlaps_range(-10, 10)
    assert iv0.overlaps_range(-10, 20)
    assert iv0.overlaps_range(0, 20)
    assert iv0.overlaps_range(5, 20)
    assert not iv0.overlaps_range(10, 20)
    assert not iv0.overlaps_range(15, 20)

    # Also test with Interval objects via overlaps_interval
    assert iv0.overlaps_interval(iv0)
    assert not iv0.overlaps_interval(Interval(-10, -5))
    assert not iv0.overlaps_interval(Interval(-10, 0))
    assert iv0.overlaps_interval(Interval(-10, 5))
    assert iv0.overlaps_interval(Interval(-10, 10))
    assert iv0.overlaps_interval(Interval(-10, 20))
    assert iv0.overlaps_interval(Interval(0, 20))
    assert iv0.overlaps_interval(Interval(5, 20))
    assert not iv0.overlaps_interval(Interval(10, 20))
    assert not iv0.overlaps_interval(Interval(15, 20))


# gt(), ge(), lt(), le(), __cmp__() are not available in manzanita -- skipped


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
