#!/usr/bin/env python3
"""
Benchmark comparing manzanita (Rust) vs intervaltree (Python).

Usage:
    pip install intervaltree
    python benchmarks/bench.py
"""

import random
import time
from contextlib import contextmanager

from manzanita import Interval as MInterval, IntervalTree as MTree

try:
    from intervaltree import Interval as PInterval, IntervalTree as PTree
except ImportError:
    print("Install intervaltree for comparison: pip install intervaltree")
    raise SystemExit(1)


@contextmanager
def timer():
    result = {}
    start = time.perf_counter()
    yield result
    result["elapsed"] = time.perf_counter() - start


def generate_intervals(n, seed=42):
    rng = random.Random(seed)
    intervals = []
    for i in range(n):
        start = rng.uniform(0, 1_000_000)
        length = rng.uniform(1, 10_000)
        intervals.append((start, start + length, f"d{i}"))
    return intervals


def bench_insertion(intervals):
    with timer() as m:
        tree = MTree()
        for b, e, d in intervals:
            tree.addi(b, e, d)
    with timer() as p:
        tree = PTree()
        for b, e, d in intervals:
            tree.addi(b, e, d)
    return m["elapsed"], p["elapsed"]


def bench_point_query(intervals, queries):
    mt = MTree()
    pt = PTree()
    for b, e, d in intervals:
        mt.addi(b, e, d)
        pt.addi(b, e, d)

    with timer() as m:
        for q in queries:
            mt.at(q)
    with timer() as p:
        for q in queries:
            pt.at(q)
    return m["elapsed"], p["elapsed"]


def bench_range_query(intervals, queries):
    mt = MTree()
    pt = PTree()
    for b, e, d in intervals:
        mt.addi(b, e, d)
        pt.addi(b, e, d)

    with timer() as m:
        for lo, hi in queries:
            mt.overlap(lo, hi)
    with timer() as p:
        for lo, hi in queries:
            pt.overlap(lo, hi)
    return m["elapsed"], p["elapsed"]


def bench_merge_overlaps(intervals):
    mt = MTree()
    pt = PTree()
    for b, e, d in intervals:
        mt.addi(b, e, d)
        pt.addi(b, e, d)

    with timer() as m:
        mt.merge_overlaps()
    with timer() as p:
        pt.merge_overlaps()
    return m["elapsed"], p["elapsed"]


def bench_removal(intervals):
    rng = random.Random(99)
    points = [rng.uniform(0, 1_000_000) for _ in range(len(intervals) // 10)]

    mt = MTree()
    pt = PTree()
    for b, e, d in intervals:
        mt.addi(b, e, d)
        pt.addi(b, e, d)

    with timer() as m:
        for q in points:
            mt.remove_overlap(q)
    with timer() as p:
        for q in points:
            pt.remove_overlap(q)
    return m["elapsed"], p["elapsed"]


def run_suite(n, n_queries):
    intervals = generate_intervals(n)
    rng = random.Random(123)
    point_queries = [rng.uniform(0, 1_000_000) for _ in range(n_queries)]
    # Narrow range queries (width ~5000, matching ~0.5% of intervals)
    range_queries = []
    for _ in range(n_queries):
        lo = rng.uniform(0, 1_000_000)
        hi = lo + rng.uniform(100, 5_000)
        range_queries.append((lo, hi))

    results = {}
    results["Insertion"] = bench_insertion(intervals)
    results["Point query"] = bench_point_query(intervals, point_queries)
    results["Range query"] = bench_range_query(intervals, range_queries)
    results["Merge overlaps"] = bench_merge_overlaps(intervals)
    results["Removal"] = bench_removal(intervals)
    return results


def format_time(t):
    if t < 0.001:
        return f"{t * 1_000_000:.0f}us"
    elif t < 1.0:
        return f"{t * 1_000:.1f}ms"
    else:
        return f"{t:.2f}s"


def main():
    sizes = [1_000, 10_000, 100_000]
    n_queries = 10_000

    print("=" * 72)
    print("Manzanita (Rust) vs intervaltree (Python) Benchmark")
    print("=" * 72)

    for n in sizes:
        q = n_queries if n <= 10_000 else 1_000
        print(f"\n--- {n:,} intervals, {q:,} queries ---\n")
        print(f"{'Operation':<20} {'manzanita':>12} {'intervaltree':>14} {'Speedup':>10}")
        print("-" * 58)

        results = run_suite(n, q)
        for op, (m, p) in results.items():
            speedup = p / m if m > 0 else float("inf")
            print(f"{op:<20} {format_time(m):>12} {format_time(p):>14} {speedup:>9.1f}x")

    print()


if __name__ == "__main__":
    main()
