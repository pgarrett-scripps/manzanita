"""
Adaptation layer for porting intervaltree tests to manzanita.

Provides helper functions that bridge API differences between
intervaltree and manzanita.
"""
from manzanita import IntervalTree, Interval


def set_data(s):
    """Extract data values from a collection of intervals.

    Replaces intervaltree's test/match.py set_data().
    """
    return {iv.data for iv in s}


def sorted_iv(iterable):
    """Sort intervals deterministically."""
    return sorted(iterable, key=lambda iv: (iv.begin, iv.end, str(iv.data)))


def make_tree_deduped(tuples):
    """Build an IntervalTree from tuples, skipping duplicates.

    Mimics intervaltree's set semantics where adding a duplicate is a no-op.
    """
    seen = set()
    t = IntervalTree()
    for tup in tuples:
        key = tuple(tup)
        if key not in seen:
            seen.add(key)
            if len(tup) == 2:
                t.addi(tup[0], tup[1])
            else:
                t.addi(tup[0], tup[1], tup[2])
    return t
