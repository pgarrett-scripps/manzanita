#!/usr/bin/env python3
"""
Comprehensive test suite to verify that intervaltree (Python) and manzanita (Rust) 
libraries behave identically for interval tree operations.
"""

import unittest
import random
import sys
from intervaltree import IntervalTree as PyIntervalTree, Interval as PyInterval
from manzanita import IntervalTree as RustIntervalTree, Interval as RustInterval


class ComprehensiveIntervalTreeTest(unittest.TestCase):
    """Test suite to ensure intervaltree and manzanita behave identically."""

    def setUp(self):
        """Set up test fixtures with various interval configurations."""
        # Basic test intervals
        self.basic_intervals = [
            (1.0, 5.5, "data1"),
            (3.3, 7.7, "data2"),
            (6.6, 9.9, "data3"),
            (2.0, 4.0, "data4"),
            (8.0, 10.0, "data5")
        ]
        
        # Edge case intervals
        self.edge_intervals = [
            (0.0, 1.0, "edge1"),
            (1.0, 1.0001, "tiny"),
            (100.0, 200.0, "large"),
            (-5.0, -1.0, "negative"),
            (0.5, 0.5001, "micro")
        ]
        
        # Overlapping intervals
        self.overlapping_intervals = [
            (1.0, 3.0, "overlap1"),
            (2.0, 4.0, "overlap2"),
            (2.5, 3.5, "overlap3"),
            (1.5, 5.0, "overlap4"),
            (0.5, 6.0, "overlap5")
        ]

    def create_trees_from_intervals(self, intervals):
        """Create both Python and Rust trees with the same intervals."""
        py_tree = PyIntervalTree()
        rust_tree = RustIntervalTree()
        
        for begin, end, data in intervals:
            # Add to Python tree using slice notation
            py_tree[begin:end] = data
            
            # Add to Rust tree using add method
            rust_tree.add(RustInterval(begin, end, data))
        
        return py_tree, rust_tree

    def extract_interval_data(self, intervals):
        """Extract (begin, end, data) tuples from interval objects."""
        return sorted((iv.begin, iv.end, iv.data) for iv in intervals)

    def test_basic_intervals(self):
        """Test basic interval operations."""
        py_tree, rust_tree = self.create_trees_from_intervals(self.basic_intervals)
        
        # Test various point queries
        test_points = [0.5, 2.0, 4.4, 6.5, 7.7, 9.5, 15.0]
        
        for point in test_points:
            with self.subTest(point=point):
                py_results = self.extract_interval_data(py_tree.at(point))
                rust_results = self.extract_interval_data(rust_tree.at(point))
                self.assertEqual(py_results, rust_results, 
                               f"Point query mismatch at {point}")

    def test_range_queries(self):
        """Test range overlap queries."""
        py_tree, rust_tree = self.create_trees_from_intervals(self.basic_intervals)
        
        # Test various range queries
        test_ranges = [
            (0.0, 2.0),
            (2.2, 6.6),
            (5.5, 8.8),
            (7.0, 12.0),
            (-1.0, 1.0),
            (10.0, 20.0)
        ]
        
        for start, end in test_ranges:
            with self.subTest(range=(start, end)):
                py_results = self.extract_interval_data(py_tree.overlap(start, end))
                rust_results = self.extract_interval_data(rust_tree.overlap(start, end))
                self.assertEqual(py_results, rust_results, 
                               f"Range query mismatch for [{start}, {end})")

    def test_edge_cases(self):
        """Test edge cases with tiny intervals, negative values, etc."""
        py_tree, rust_tree = self.create_trees_from_intervals(self.edge_intervals)
        
        # Test edge case points
        test_points = [-10.0, -2.5, 0.0, 0.5, 1.0, 1.00005, 150.0, 300.0]
        
        for point in test_points:
            with self.subTest(point=point):
                py_results = self.extract_interval_data(py_tree.at(point))
                rust_results = self.extract_interval_data(rust_tree.at(point))
                self.assertEqual(py_results, rust_results, 
                               f"Edge case point query mismatch at {point}")

    def test_overlapping_intervals(self):
        """Test with heavily overlapping intervals."""
        py_tree, rust_tree = self.create_trees_from_intervals(self.overlapping_intervals)
        
        # Test points in overlapping regions
        test_points = [1.5, 2.5, 3.0, 3.5, 4.5]
        
        for point in test_points:
            with self.subTest(point=point):
                py_results = self.extract_interval_data(py_tree.at(point))
                rust_results = self.extract_interval_data(rust_tree.at(point))
                self.assertEqual(py_results, rust_results, 
                               f"Overlapping intervals point query mismatch at {point}")

    def test_slice_notation_access(self):
        """Test accessing intervals using slice notation tree[point] and tree[start:end]."""
        py_tree, rust_tree = self.create_trees_from_intervals(self.basic_intervals)
        
        # Test point access with bracket notation
        test_points = [2.0, 4.4, 7.7]
        for point in test_points:
            with self.subTest(point=point):
                py_results = self.extract_interval_data(py_tree[point])
                rust_results = self.extract_interval_data(rust_tree[point])
                self.assertEqual(py_results, rust_results, 
                               f"Slice notation point access mismatch at {point}")
        
        # Test range access with bracket notation
        test_ranges = [(2.2, 6.6), (5.5, 8.8)]
        for start, end in test_ranges:
            with self.subTest(range=(start, end)):
                py_results = self.extract_interval_data(py_tree[start:end])
                rust_results = self.extract_interval_data(rust_tree[start:end])
                self.assertEqual(py_results, rust_results, 
                               f"Slice notation range access mismatch for [{start}:{end}]")

    def test_tree_length(self):
        """Test that both trees report the same length."""
        for intervals in [self.basic_intervals, self.edge_intervals, self.overlapping_intervals]:
            with self.subTest(intervals=len(intervals)):
                py_tree, rust_tree = self.create_trees_from_intervals(intervals)
                self.assertEqual(len(py_tree), len(rust_tree), 
                               f"Tree length mismatch for {len(intervals)} intervals")

    def test_empty_tree(self):
        """Test behavior with empty trees."""
        py_tree = PyIntervalTree()
        rust_tree = RustIntervalTree()
        
        # Test point queries on empty tree
        self.assertEqual(list(py_tree.at(5.0)), list(rust_tree.at(5.0)))
        
        # Test range queries on empty tree
        self.assertEqual(list(py_tree.overlap(1.0, 10.0)), list(rust_tree.overlap(1.0, 10.0)))
        
        # Test length of empty tree
        self.assertEqual(len(py_tree), len(rust_tree))
        self.assertEqual(len(py_tree), 0)

    def test_duplicate_intervals(self):
        """Test behavior with duplicate intervals."""
        intervals_with_duplicates = [
            (1.0, 3.0, "dup1"),
            (1.0, 3.0, "dup2"),  # Same interval, different data
            (2.0, 4.0, "unique"),
            (1.0, 3.0, "dup3"),  # Another duplicate
        ]
        
        py_tree, rust_tree = self.create_trees_from_intervals(intervals_with_duplicates)
        
        # Test point query
        py_results = self.extract_interval_data(py_tree.at(2.0))
        rust_results = self.extract_interval_data(rust_tree.at(2.0))
        self.assertEqual(py_results, rust_results, "Duplicate intervals point query mismatch")
        
        # Test that all duplicates are present
        self.assertEqual(len(py_tree), len(rust_tree))

    def test_random_intervals(self):
        """Test with randomly generated intervals."""
        random.seed(42)  # For reproducible tests
        
        # Generate random intervals
        random_intervals = []
        for _ in range(50):
            start = random.uniform(0, 100)
            length = random.uniform(0.1, 20)
            end = start + length
            data = f"random_{len(random_intervals)}"
            random_intervals.append((start, end, data))
        
        py_tree, rust_tree = self.create_trees_from_intervals(random_intervals)
        
        # Test random point queries
        for _ in range(20):
            point = random.uniform(-10, 110)
            with self.subTest(point=point):
                py_results = self.extract_interval_data(py_tree.at(point))
                rust_results = self.extract_interval_data(rust_tree.at(point))
                self.assertEqual(py_results, rust_results, 
                               f"Random test point query mismatch at {point}")
        
        # Test random range queries
        for _ in range(20):
            start = random.uniform(-10, 100)
            end = start + random.uniform(1, 30)
            with self.subTest(range=(start, end)):
                py_results = self.extract_interval_data(py_tree.overlap(start, end))
                rust_results = self.extract_interval_data(rust_tree.overlap(start, end))
                self.assertEqual(py_results, rust_results, 
                               f"Random test range query mismatch for [{start}, {end})")

    def test_iteration(self):
        """Test iteration over both trees."""
        py_tree, rust_tree = self.create_trees_from_intervals(self.basic_intervals)
        
        # Get all intervals by iteration
        py_all = self.extract_interval_data(py_tree)
        rust_all = self.extract_interval_data(rust_tree)
        
        self.assertEqual(py_all, rust_all, "Tree iteration results differ")

    def test_boundary_conditions(self):
        """Test boundary conditions for interval endpoints."""
        boundary_intervals = [
            (1.0, 2.0, "boundary1"),
            (2.0, 3.0, "boundary2"),  # Shares endpoint with previous
            (1.5, 2.5, "boundary3"),  # Overlaps both
        ]
        
        py_tree, rust_tree = self.create_trees_from_intervals(boundary_intervals)
        
        # Test queries at exact boundary points
        boundary_points = [1.0, 1.5, 2.0, 2.5, 3.0]
        for point in boundary_points:
            with self.subTest(point=point):
                py_results = self.extract_interval_data(py_tree.at(point))
                rust_results = self.extract_interval_data(rust_tree.at(point))
                self.assertEqual(py_results, rust_results, 
                               f"Boundary condition mismatch at {point}")

    def test_mixed_data_types(self):
        """Test with different data types as interval data."""
        mixed_intervals = [
            (1.0, 2.0, "string_data"),
            (2.0, 3.0, 42),
            (3.0, 4.0, [1, 2, 3]),
            (4.0, 5.0, {"key": "value"}),
            (5.0, 6.0, None),
        ]
        
        py_tree, rust_tree = self.create_trees_from_intervals(mixed_intervals)
        
        # Test point queries
        test_points = [1.5, 2.5, 3.5, 4.5, 5.5]
        for point in test_points:
            with self.subTest(point=point):
                py_results = self.extract_interval_data(py_tree.at(point))
                rust_results = self.extract_interval_data(rust_tree.at(point))
                self.assertEqual(py_results, rust_results, 
                               f"Mixed data types mismatch at {point}")


def run_comprehensive_test():
    """Run the comprehensive test suite and report results."""
    print("Running comprehensive interval tree comparison tests...")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(ComprehensiveIntervalTreeTest)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED! intervaltree and manzanita behave identically.")
    else:
        print("❌ SOME TESTS FAILED! There are behavioral differences.")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
