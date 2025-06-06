#!/usr/bin/env python3
"""
Basic functionality tests for the manzanita interval tree.
Tests core operations like creation, insertion, and basic queries.
"""

import unittest
from manzanita import IntervalTree, Interval
from .test_utils import create_basic_intervals, create_tree_from_tuples, extract_interval_data


class TestBasicFunctionality(unittest.TestCase):
    """Test basic interval tree operations."""

    def setUp(self):
        """Set up basic test fixtures."""
        self.intervals = create_basic_intervals()
        self.tree = create_tree_from_tuples(self.intervals)

    def test_tree_creation_empty(self):
        """Test creating an empty interval tree."""
        tree = IntervalTree()
        self.assertEqual(len(tree), 0)
        self.assertTrue(tree.is_empty())
        self.assertFalse(tree)  # Test __bool__

    def test_tree_creation_with_intervals(self):
        """Test creating a tree with initial intervals."""
        intervals = [Interval(1.0, 3.0, "test")]
        tree = IntervalTree(intervals)
        self.assertEqual(len(tree), 1)
        self.assertFalse(tree.is_empty())
        self.assertTrue(tree)  # Test __bool__

    def test_tree_from_tuples(self):
        """Test creating a tree using from_tuples constructor."""
        tuples = [(1.0, 3.0, "a"), (2.0, 4.0, "b")]
        tree = IntervalTree.from_tuples(tuples)
        self.assertEqual(len(tree), 2)
        
        # Verify intervals were added correctly
        all_intervals = extract_interval_data(tree)
        expected = sorted(tuples)
        self.assertEqual(all_intervals, expected)

    def test_interval_creation(self):
        """Test creating intervals."""
        interval = Interval(1.0, 3.0, "test_data")
        self.assertEqual(interval.begin, 1.0)
        self.assertEqual(interval.end, 3.0)
        self.assertEqual(interval.data, "test_data")

    def test_add_interval(self):
        """Test adding intervals to the tree."""
        tree = IntervalTree()
        interval = Interval(1.0, 3.0, "test")
        
        tree.add(interval)
        self.assertEqual(len(tree), 1)
        
        # Add another interval
        tree.add(Interval(2.0, 4.0, "test2"))
        self.assertEqual(len(tree), 2)

    def test_addi_method(self):
        """Test adding interval using addi method (begin, end, data)."""
        tree = IntervalTree()
        tree.addi(1.0, 3.0, "test")
        
        self.assertEqual(len(tree), 1)
        results = list(tree.at(2.0))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].data, "test")

    def test_basic_point_query(self):
        """Test querying intervals at a specific point."""
        # Test point that intersects multiple intervals
        results = list(self.tree.at(4.0))
        self.assertGreater(len(results), 0)
        
        # All returned intervals should contain the query point
        for interval in results:
            self.assertLessEqual(interval.begin, 4.0)
            self.assertGreater(interval.end, 4.0)

    def test_slice_notation_point_query(self):
        """Test point query using slice notation tree[point]."""
        results_at = list(self.tree.at(4.0))
        results_slice = list(self.tree[4.0])
        
        # Should return the same results
        at_data = extract_interval_data(results_at)
        slice_data = extract_interval_data(results_slice)
        self.assertEqual(at_data, slice_data)

    def test_basic_range_query(self):
        """Test querying intervals that overlap a range."""
        results = list(self.tree.overlap(3.0, 6.0))
        self.assertGreater(len(results), 0)
        
        # All returned intervals should overlap with [3.0, 6.0)
        for interval in results:
            # Intervals overlap if: interval.begin < range_end and interval.end > range_begin
            self.assertLess(interval.begin, 6.0)
            self.assertGreater(interval.end, 3.0)

    def test_slice_notation_range_query(self):
        """Test range query using slice notation tree[begin:end]."""
        results_overlap = list(self.tree.overlap(3.0, 6.0))
        results_slice = list(self.tree[3.0:6.0])
        
        # Should return the same results
        overlap_data = extract_interval_data(results_overlap)
        slice_data = extract_interval_data(results_slice)
        self.assertEqual(overlap_data, slice_data)

    def test_envelop_query(self):
        """Test envelop query (intervals completely contained within range)."""
        # Add a small interval that should be enveloped
        self.tree.add(Interval(3.5, 4.5, "small"))
        
        results = list(self.tree.envelop(3.0, 5.0))
        
        # All returned intervals should be completely within [3.0, 5.0]
        for interval in results:
            self.assertGreaterEqual(interval.begin, 3.0)
            self.assertLessEqual(interval.end, 5.0)

    def test_tree_length(self):
        """Test len() function on tree."""
        expected_length = len(self.intervals)
        self.assertEqual(len(self.tree), expected_length)

    def test_tree_boundaries(self):
        """Test begin() and end() methods."""
        if not self.tree.is_empty():
            tree_begin = self.tree.begin()
            tree_end = self.tree.end()
            
            # Find expected boundaries from our test data
            all_begins = [begin for begin, end, data in self.intervals]
            all_ends = [end for begin, end, data in self.intervals]
            
            expected_begin = min(all_begins)
            expected_end = max(all_ends)
            
            self.assertEqual(tree_begin, expected_begin)
            self.assertEqual(tree_end, expected_end)

    def test_iteration(self):
        """Test iterating over all intervals in the tree."""
        all_intervals = list(self.tree)
        self.assertEqual(len(all_intervals), len(self.intervals))
        
        # Convert to tuples for comparison
        actual_data = extract_interval_data(all_intervals)
        expected_data = sorted(self.intervals)
        self.assertEqual(actual_data, expected_data)

    def test_items_method(self):
        """Test the items() method."""
        items_result = list(self.tree.items())
        iter_result = list(self.tree)
        
        # items() and direct iteration should return the same results
        items_data = extract_interval_data(items_result)
        iter_data = extract_interval_data(iter_result)
        self.assertEqual(items_data, iter_data)

    
    def test_contains_interval(self):
        """Test checking if interval is in tree using 'in' operator."""
        interval = Interval(1.0, 3.0, "test")
        tree = IntervalTree()
        
        # Interval not in empty tree
        self.assertFalse(interval in tree)
        
        # Add interval and check
        tree.add(interval)
        self.assertTrue(interval in tree)

    def test_containsi_method(self):
        """Test checking if interval is in tree using containsi method."""
        tree = IntervalTree()
        tree.addi(1.0, 3.0, "test")
        
        # Check using individual parameters
        self.assertTrue(tree.containsi(1.0, 3.0, "test"))
        self.assertFalse(tree.containsi(1.0, 3.0, "different"))

    def test_overlaps_point(self):
        """Test checking if any intervals overlap with a point."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 3.0, "test"))
        
        self.assertTrue(tree.overlaps(2.0))    # Point inside interval
        self.assertFalse(tree.overlaps(5.0))   # Point outside interval

    def test_overlaps_range(self):
        """Test checking if any intervals overlap with a range."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 3.0, "test"))
        
        self.assertTrue(tree.overlaps(2.0, 4.0))   # Range overlaps
        self.assertFalse(tree.overlaps(5.0, 7.0)) # Range doesn't overlap

    def test_slice_assignment(self):
        """Test adding intervals using slice assignment tree[start:end] = data."""
        tree = IntervalTree()
        
        # Add interval using slice notation
        tree[1.0:3.0] = "test_data"
        self.assertEqual(len(tree), 1)
        
        # Check the interval was added correctly
        results = list(tree.at(2.0))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].data, "test_data")

    def test_remove_interval(self):
        """Test removing intervals using remove() method."""
        tree = IntervalTree()
        interval = Interval(1.0, 3.0, "test")
        tree.add(interval)
        
        # Remove the interval
        tree.remove(interval)
        self.assertEqual(len(tree), 0)
        
        # Try to remove non-existent interval (should raise ValueError)
        with self.assertRaises(ValueError):
            tree.remove(interval)

    def test_discard_interval(self):
        """Test removing intervals using discard() method."""
        tree = IntervalTree()
        interval = Interval(1.0, 3.0, "test")
        tree.add(interval)
        
        # Discard the interval
        tree.discard(interval)
        self.assertEqual(len(tree), 0)
        
        # Try to discard non-existent interval (should not raise error)
        tree.discard(interval)  # Should do nothing quietly

    def test_removei_method(self):
        """Test removing intervals using removei() method."""
        tree = IntervalTree()
        tree.addi(1.0, 3.0, "test")
        
        # Remove using individual parameters
        tree.removei(1.0, 3.0, "test")
        self.assertEqual(len(tree), 0)
        
        # Try to remove non-existent interval (should raise ValueError)
        with self.assertRaises(ValueError):
            tree.removei(1.0, 3.0, "test")

    def test_discardi_method(self):
        """Test removing intervals using discardi() method."""
        tree = IntervalTree()
        tree.addi(1.0, 3.0, "test")
        
        # Discard using individual parameters
        tree.discardi(1.0, 3.0, "test")
        self.assertEqual(len(tree), 0)
        
        # Try to discard non-existent interval (should not raise error)
        tree.discardi(1.0, 3.0, "test")  # Should do nothing quietly

    def test_remove_overlap_point(self):
        """Test removing all intervals overlapping a point."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 4.0, "a"))
        tree.add(Interval(3.0, 6.0, "b"))
        tree.add(Interval(7.0, 9.0, "c"))
        
        # Remove all intervals overlapping point 3.5
        tree.remove_overlap(3.5)
        
        # Should only have the non-overlapping interval left
        remaining = list(tree)
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].data, "c")

    def test_remove_overlap_range(self):
        """Test removing all intervals overlapping a range."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 3.0, "a"))
        tree.add(Interval(2.0, 5.0, "b"))
        tree.add(Interval(6.0, 8.0, "c"))
        
        # Remove all intervals overlapping range [2.5, 6.5)
        tree.remove_overlap(2.5, 6.5)
        
        # Should only have the first interval left
        remaining = list(tree)
        self.assertEqual(len(remaining), 0)

    def test_remove_envelop(self):
        """Test removing all intervals enveloped by a range."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 6.0, "big"))
        tree.add(Interval(2.0, 4.0, "small"))
        tree.add(Interval(3.0, 5.0, "medium"))
        
        # Remove all intervals enveloped by [1.5, 5.5)
        tree.remove_envelop(1.5, 5.5)
        
        # Should only have the big interval left
        remaining = list(tree)
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].data, "big")

    def test_clear_method(self):
        """Test clearing all intervals from tree."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 3.0, "test1"))
        tree.add(Interval(2.0, 4.0, "test2"))
        
        # Clear the tree
        tree.clear()
        self.assertEqual(len(tree), 0)
        self.assertTrue(tree.is_empty())

    def test_del_point_syntax(self):
        """Test deleting intervals using del tree[point] syntax."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 4.0, "a"))
        tree.add(Interval(3.0, 6.0, "b"))
        tree.add(Interval(7.0, 9.0, "c"))
        
        # Delete all intervals overlapping point 3.5
        del tree[3.5]
        
        # Should only have the non-overlapping interval left
        remaining = list(tree)
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].data, "c")

    def test_del_range_syntax(self):
        """Test deleting intervals using del tree[start:end] syntax."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 3.0, "a"))
        tree.add(Interval(2.0, 5.0, "b"))
        tree.add(Interval(6.0, 8.0, "c"))
        
        # Delete all intervals overlapping range [2.5:6.5]
        del tree[2.5:6.5]
        
        # Should only have the first interval left
        remaining = list(tree)
        self.assertEqual(len(remaining), 0)
