# Ported from intervaltree test/interval_methods/unary_test.py
"""
Test module: Intervals, methods on self only

NOTE: is_null(), length(), _get_fields() are not available in manzanita.
      Null intervals (begin >= end) raise ValueError in manzanita.
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


# length(), _get_fields() are not available in manzanita -- skipped


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
