#!/usr/bin/env python3
"""
Test utilities and fixtures for manzanita interval tree tests.
"""

import random
from typing import List, Tuple, Any
from manzanita import IntervalTree, Interval


def create_basic_intervals() -> List[Tuple[float, float, str]]:
    """Create a standard set of test intervals."""
    return [
        (1.0, 5.5, "data1"),
        (3.3, 7.7, "data2"),
        (6.6, 9.9, "data3"),
        (2.0, 4.0, "data4"),
        (8.0, 10.0, "data5")
    ]


def create_overlapping_intervals() -> List[Tuple[float, float, str]]:
    """Create intervals that heavily overlap."""
    return [
        (1.0, 3.0, "overlap1"),
        (2.0, 4.0, "overlap2"),
        (2.5, 3.5, "overlap3"),
        (1.5, 5.0, "overlap4"),
        (0.5, 6.0, "overlap5")
    ]


def create_edge_case_intervals() -> List[Tuple[float, float, str]]:
    """Create intervals with edge cases (tiny, negative, large)."""
    return [
        (0.0, 1.0, "edge1"),
        (1.0, 1.0001, "tiny"),
        (100.0, 200.0, "large"),
        (-5.0, -1.0, "negative"),
        (0.5, 0.5001, "micro")
    ]


def create_tree_from_tuples(intervals: List[Tuple[float, float, Any]]) -> IntervalTree:
    """Create an IntervalTree from a list of (begin, end, data) tuples."""
    tree = IntervalTree()
    for begin, end, data in intervals:
        tree.add(Interval(begin, end, data))
    return tree


def extract_interval_data(intervals) -> List[Tuple[float, float, Any]]:
    """Extract (begin, end, data) tuples from interval objects and sort them."""
    return sorted((iv.begin, iv.end, iv.data) for iv in intervals)


def generate_random_intervals(count: int = 50, seed: int = 42) -> List[Tuple[float, float, str]]:
    """Generate random intervals for stress testing."""
    random.seed(seed)
    intervals = []
    for i in range(count):
        start = random.uniform(0, 100)
        length = random.uniform(0.1, 20)
        end = start + length
        data = f"random_{i}"
        intervals.append((start, end, data))
    return intervals
