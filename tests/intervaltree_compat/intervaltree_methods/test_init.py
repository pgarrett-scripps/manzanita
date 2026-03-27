# Ported from intervaltree test/intervaltree_methods/init_test.py
"""
Test module: IntervalTree, initialization methods
"""
from manzanita import Interval, IntervalTree
import pytest


def test_empty_init():
    tree = IntervalTree()
    assert not tree
    assert len(tree) == 0
    assert list(tree) == []
    assert tree.is_empty()


def test_list_init():
    tree = IntervalTree([Interval(-10, 10), Interval(-20.0, -10.0)])
    assert tree
    assert len(tree) == 2
    assert set(tree.items()) == set([Interval(-10, 10), Interval(-20.0, -10.0)])
    assert tree.begin() == -20
    assert tree.end() == 10


def test_generator_init():
    tree = IntervalTree(
        [Interval(begin, end) for begin, end in
        [(-10, 10), (-20, -10), (10, 20)]]
    )
    assert tree
    assert len(tree) == 3
    assert set(tree.items()) == set([
        Interval(-20, -10),
        Interval(-10, 10),
        Interval(10, 20),
    ])
    assert tree.begin() == -20
    assert tree.end() == 20


def test_invalid_interval_init():
    """
    Ensure that begin < end.
    """
    with pytest.raises(ValueError):
        Interval(-1, -2)

    with pytest.raises(ValueError):
        Interval(0, 0)

    with pytest.raises(ValueError):
        Interval(1, 0)

    with pytest.raises(ValueError):
        Interval(1, 1)


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
