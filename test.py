import unittest
from intervaltree import IntervalTree as PyIntervalTree
from manzanita import IntervalTree as RustIntervalTree, Interval


class TestIntervalTrees(unittest.TestCase):

    def setUp(self):
        # Set up the same intervals for both trees
        self.intervals = [
            (1.0, 5.5, "data1"),
            (3.3, 7.7, "data2"),
            (6.6, 9.9, "data3")
        ]

        # Python interval tree
        self.py_tree = PyIntervalTree()
        for begin, end, data in self.intervals:
            self.py_tree[begin:end] = data

        # Rust-backed interval tree (manzanita)
        self.rust_tree = RustIntervalTree()
        for begin, end, data in self.intervals:
            interval = Interval(begin, end, data)
            self.rust_tree.add(interval)

    def test_point_queries(self):
        # Test point query for both trees
        points_to_test = [4.4, 7.7]

        for point in points_to_test:
            # Python interval tree
            py_results = sorted((iv.begin, iv.end, iv.data) for iv in self.py_tree.at(point))

            # Rust interval tree
            rust_results = sorted((iv.begin, iv.end, iv.data) for iv in self.rust_tree.at(point))

            # Assert that both trees return the same intervals
            self.assertEqual(py_results, rust_results, f"Mismatch at point {point}")

    def test_range_queries(self):
        # Test range queries for both trees
        ranges_to_test = [
            (2.2, 6.6),
            (5.5, 8.8)
        ]

        for start, end in ranges_to_test:
            # Python interval tree
            py_results = sorted((iv.begin, iv.end, iv.data) for iv in self.py_tree.overlap(start, end))

            # Rust interval tree
            rust_results = sorted((iv.begin, iv.end, iv.data) for iv in self.rust_tree.overlap(start, end))

            # Assert that both trees return the same intervals
            self.assertEqual(py_results, rust_results, f"Mismatch in range {start} - {end}")


if __name__ == '__main__':
    unittest.main()
