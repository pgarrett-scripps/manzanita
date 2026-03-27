# Ported from intervaltree test/interval_methods/binary_test.py
"""
Test module: Intervals, methods on two intervals

NOTE: overlap_size() and distance_to() are not available in manzanita.
      contains_interval() is mapped to enveloped_by_interval() (reversed).
      overlaps(other_iv) is mapped to overlaps_interval(other_iv).
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


# overlap_size() is not available in manzanita -- skipped


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
    """
    intervaltree's iv.contains_interval(other) is equivalent to
    other.enveloped_by(iv.begin, iv.end) in manzanita.

    NOTE: enveloped_by_interval() uses boundary inclusivity checks which
    differ for half-open intervals, so we use enveloped_by(begin, end) instead.
    """
    def contains(container, contained):
        return contained.enveloped_by(container.begin, container.end)

    # iv0 contains iv0
    assert contains(iv0, iv0)
    # iv0 does not contain iv1..iv9
    assert not contains(iv0, iv1)
    assert not contains(iv0, iv2)
    assert not contains(iv0, iv3)
    assert not contains(iv0, iv4)
    assert not contains(iv0, iv5)
    assert not contains(iv0, iv6)
    assert not contains(iv0, iv7)
    assert not contains(iv0, iv8)
    assert not contains(iv0, iv9)
    assert not contains(iv0, iv10)

    # iv2 contains iv1, iv2, iv10
    assert not contains(iv2, iv0)
    assert contains(iv2, iv1)
    assert contains(iv2, iv2)
    assert not contains(iv2, iv3)
    assert not contains(iv2, iv4)
    assert not contains(iv2, iv5)
    assert not contains(iv2, iv6)
    assert not contains(iv2, iv7)
    assert not contains(iv2, iv8)
    assert not contains(iv2, iv9)
    assert contains(iv2, iv10)


# distance_to() is not available in manzanita -- skipped


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
