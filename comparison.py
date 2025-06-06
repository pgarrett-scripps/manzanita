import time
import random
from intervaltree import Interval, IntervalTree
from manzanita import Interval as MInterval, IntervalTree as MIntervalTree

# Parameters for the test
NUM_INTERVALS = 100_000  # Number of intervals to insert
NUM_QUERIES = 10_000  # Number of queries to perform
RANGE_START = 200
RANGE_END = 2000
QUERY_RANGE = 1  # Range size for range queries


# Generate random intervals
def generate_intervals(num_intervals, range_start, range_end):
    intervals = []
    for _ in range(num_intervals):
        begin = random.uniform(range_start, range_end)
        length = random.uniform(0.01, 2)
        end = begin + length
        intervals.append((begin, end))
    return intervals


# Generate random points for queries
def generate_points(num_queries, range_start, range_end):
    return [random.uniform(range_start, range_end) for _ in range(num_queries)]


# Benchmark function
def benchmark():
    print(f"Generating {NUM_INTERVALS} random intervals...")
    intervals = generate_intervals(NUM_INTERVALS, RANGE_START, RANGE_END)

    print("Generating random query points...")
    query_points = generate_points(NUM_QUERIES, RANGE_START, RANGE_END)

    print("\nTesting intervaltree (Python)...")
    # Initialize intervaltree
    py_tree = IntervalTree()

    # Insert intervals
    start_time = time.time()
    for begin, end in intervals:
        py_tree.add(Interval(begin, end))
    insert_time_py = time.time() - start_time
    print(f"Insertion time: {insert_time_py:.4f} seconds")

    # Point queries
    start_time = time.time()
    for point in query_points:
        _ = py_tree.at(point)
    point_query_time_py = time.time() - start_time
    print(f"Point query time: {point_query_time_py:.4f} seconds")

    # Range queries
    start_time = time.time()
    for point in query_points[:100]:
        begin = point
        end = point + QUERY_RANGE
        _ = py_tree.overlap(begin, end)
    range_query_time_py = time.time() - start_time
    print(f"Range query time: {range_query_time_py:.4f} seconds")

    print("\nTesting manzanita (Rust backend)...")
    # Initialize manzanita
    rust_tree = MIntervalTree()

    # Insert intervals
    start_time = time.time()
    for begin, end in intervals:
        rust_tree.add(MInterval(begin, end, None))
    insert_time_rust = time.time() - start_time
    print(f"Insertion time: {insert_time_rust:.4f} seconds")

    # Point queries
    start_time = time.time()
    for point in query_points:
        _ = rust_tree.at(point)
    point_query_time_rust = time.time() - start_time
    print(f"Point query time: {point_query_time_rust:.4f} seconds")

    # Range queries
    start_time = time.time()
    for point in query_points[:100]:
        begin = point
        end = point + QUERY_RANGE
        _ = rust_tree.overlap(begin, end)
    range_query_time_rust = time.time() - start_time
    print(f"Range query time: {range_query_time_rust:.4f} seconds")

    # Summary
    print("\nPerformance Summary:")
    print(f"Interval Insertion:")
    print(f"  intervaltree: {insert_time_py:.4f} seconds")
    print(f"  manzanita   : {insert_time_rust:.4f} seconds")

    print(f"\nPoint Queries:")
    print(f"  intervaltree: {point_query_time_py:.4f} seconds")
    print(f"  manzanita   : {point_query_time_rust:.4f} seconds")

    print(f"\nRange Queries:")
    print(f"  intervaltree: {range_query_time_py:.4f} seconds")
    print(f"  manzanita   : {range_query_time_rust:.4f} seconds")


if __name__ == "__main__":
    benchmark()
