# Ported from intervaltree test/interval_methods/unary_test.py
"""
Test module: Intervals, methods on self only

NOTE: Null intervals (begin >= end) raise ValueError in manzanita.
"""
from manzanita import Interval
import pytest


def test_isnull_not_supported():
    """manzanita rejects null intervals -- begin must be < end."""
    with pytest.raises(ValueError):
        Interval(0, 0)

    with pytest.raises(ValueError):
        Interval(1, 0)


def test_len():
    """Interval len() returns 3 (begin, end, data)."""
    iv = Interval(0, 1)
    assert len(iv) == 3

    iv = Interval(0, 1, 2)
    assert len(iv) == 3

    iv = Interval(1.3, 2.2)
    assert len(iv) == 3


def test_length():
    iv = Interval(0, 3)
    assert iv.length() == 3

    iv = Interval(-1, 1, 'data')
    assert iv.length() == 2

    iv = Interval(0.1, 3)
    assert abs(iv.length() - 2.9) < 1e-10


def test_copy():
    iv0 = Interval(1, 2, 3)
    iv1 = iv0.copy()
    assert iv1.begin == iv0.begin
    assert iv1.end == iv0.end
    assert iv1.data == iv0.data
    assert iv1 == iv0


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
