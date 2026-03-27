# Ported from intervaltree test/interval_methods/str_test.py
"""
Test module: Intervals, string representation

NOTE: manzanita's Interval repr format may differ from intervaltree's.
      These tests verify that str/repr contain the expected values.
"""
from manzanita import Interval


def test_str():
    iv = Interval(0, 1)
    s = str(iv)
    assert '0' in s
    assert '1' in s
    assert repr(iv) == s

    iv = Interval(0, 1, '[0,1)')
    s = str(iv)
    assert '0' in s
    assert '1' in s
    assert repr(iv) == s


# Subclass tests are not applicable -- manzanita Interval is a PyO3 class


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])
