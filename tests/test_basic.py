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

    def test_union_operation(self):
        """Test union operation with | operator and union() method."""
        tree1 = IntervalTree()
        tree1.add(Interval(1.0, 3.0, "a"))
        tree1.add(Interval(4.0, 6.0, "b"))
        
        tree2 = IntervalTree()
        tree2.add(Interval(2.0, 4.0, "c"))
        tree2.add(Interval(7.0, 9.0, "d"))
        
        # Test union method
        union_tree = tree1.union(tree2)
        self.assertEqual(len(union_tree), 4)
        
        # Test | operator
        union_tree2 = tree1 | tree2
        self.assertEqual(len(union_tree2), 4)

    def test_update_operation(self):
        """Test update() method and |= operator."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 3.0, "a"))
        
        intervals = [Interval(2.0, 4.0, "b"), Interval(5.0, 7.0, "c")]
        tree.update(intervals)
        self.assertEqual(len(tree), 3)

    def test_difference_operation(self):
        """Test difference operation with - operator and difference() method."""
        tree1 = IntervalTree()
        tree1.add(Interval(1.0, 3.0, "a"))
        tree1.add(Interval(4.0, 6.0, "b"))
        tree1.add(Interval(7.0, 9.0, "c"))
        
        tree2 = IntervalTree()
        tree2.add(Interval(4.0, 6.0, "b"))  # Same interval to remove
        
        # Test difference method
        diff_tree = tree1.difference(tree2)
        self.assertEqual(len(diff_tree), 2)
        
        # Test - operator
        diff_tree2 = tree1 - tree2
        self.assertEqual(len(diff_tree2), 2)

    def test_intersection_operation(self):
        """Test intersection operation with & operator and intersection() method."""
        tree1 = IntervalTree()
        tree1.add(Interval(1.0, 3.0, "a"))
        tree1.add(Interval(4.0, 6.0, "b"))
        tree1.add(Interval(7.0, 9.0, "c"))
        
        tree2 = IntervalTree()
        tree2.add(Interval(4.0, 6.0, "b"))  # Same interval
        tree2.add(Interval(10.0, 12.0, "d"))  # Different interval
        
        # Test intersection method
        intersect_tree = tree1.intersection(tree2)
        self.assertEqual(len(intersect_tree), 1)
        
        # Test & operator
        intersect_tree2 = tree1 & tree2
        self.assertEqual(len(intersect_tree2), 1)

    def test_symmetric_difference_operation(self):
        """Test symmetric difference operation with ^ operator."""
        tree1 = IntervalTree()
        tree1.add(Interval(1.0, 3.0, "a"))
        tree1.add(Interval(4.0, 6.0, "b"))
        
        tree2 = IntervalTree()
        tree2.add(Interval(4.0, 6.0, "b"))  # Same interval
        tree2.add(Interval(7.0, 9.0, "c"))  # Different interval
        
        # Test symmetric_difference method
        sym_diff_tree = tree1.symmetric_difference(tree2)
        self.assertEqual(len(sym_diff_tree), 2)  # "a" and "c"
        
        # Test ^ operator
        sym_diff_tree2 = tree1 ^ tree2
        self.assertEqual(len(sym_diff_tree2), 2)

    def test_subset_superset_operations(self):
        """Test subset and superset operations."""
        tree1 = IntervalTree()
        tree1.add(Interval(1.0, 3.0, "a"))
        
        tree2 = IntervalTree()
        tree2.add(Interval(1.0, 3.0, "a"))
        tree2.add(Interval(4.0, 6.0, "b"))
        
        # Test subset
        self.assertTrue(tree1.issubset(tree2))
        self.assertTrue(tree1 <= tree2)
        self.assertTrue(tree1 < tree2)  # proper subset
        
        # Test superset
        self.assertTrue(tree2.issuperset(tree1))
        self.assertTrue(tree2 >= tree1)
        self.assertTrue(tree2 > tree1)  # proper superset

    def test_equality_operation(self):
        """Test equality operation."""
        tree1 = IntervalTree()
        tree1.add(Interval(1.0, 3.0, "a"))
        tree1.add(Interval(4.0, 6.0, "b"))
        
        tree2 = IntervalTree()
        tree2.add(Interval(1.0, 3.0, "a"))
        tree2.add(Interval(4.0, 6.0, "b"))
        
        tree3 = IntervalTree()
        tree3.add(Interval(1.0, 3.0, "a"))
        
        self.assertTrue(tree1 == tree2)
        self.assertFalse(tree1 == tree3)

    def test_chop_operation(self):
        """Test chopping out a range from the tree."""
        tree = IntervalTree()
        tree.add(Interval(0.0, 10.0, "big"))
        tree.add(Interval(2.0, 4.0, "small"))
        tree.add(Interval(12.0, 15.0, "separate"))
        
        # Chop out the middle section
        tree.chop(3.0, 7.0)

        # Should have: [0,3), [7,10), [2,3), [12,15)
        remaining = sorted(tree.items(), key=lambda i: i.begin)
        self.assertEqual(len(remaining), 4)

        # Check the split intervals - they should preserve original boundary inclusivity
        # Original "big" interval was [0, 10) so splits should be [0, 3) and [7, 10)
        big_left = next(iv for iv in remaining if iv.begin == 0.0)
        self.assertEqual(big_left.begin, 0.0)
        self.assertEqual(big_left.end, 3.0)
        self.assertEqual(big_left.data, "big")
        self.assertTrue(big_left.start_inclusive)  # Should preserve original start inclusivity
        self.assertFalse(big_left.end_inclusive)   # End at chop point is exclusive

        big_right = next(iv for iv in remaining if iv.begin == 7.0)
        self.assertEqual(big_right.begin, 7.0)
        self.assertEqual(big_right.end, 10.0)
        self.assertEqual(big_right.data, "big")
        self.assertTrue(big_right.start_inclusive)  # Start at chop point is inclusive
        self.assertFalse(big_right.end_inclusive)   # Should preserve original end inclusivity

        # Original "small" interval was [2, 4) so only left part [2, 3) should remain
        small_left = next(iv for iv in remaining if iv.begin == 2.0)
        self.assertEqual(small_left.begin, 2.0)
        self.assertEqual(small_left.end, 3.0)
        self.assertEqual(small_left.data, "small")
        self.assertTrue(small_left.start_inclusive)  # Should preserve original start inclusivity
        self.assertFalse(small_left.end_inclusive)   # End at chop point is exclusive

        # The separate interval should be unchanged
        separate = next(iv for iv in remaining if iv.begin == 12.0)
        self.assertEqual(separate.begin, 12.0)
        self.assertEqual(separate.end, 15.0)
        self.assertEqual(separate.data, "separate")

    def test_chop_with_datafunc(self):
        """Test chopping with a data function."""
        tree = IntervalTree()
        tree.add(Interval(0.0, 10.0, "original"))
        
        def datafunc(interval, islower):
            return f"side: {'left' if islower else 'right'}"
        
        tree.chop(3.0, 7.0, datafunc)
        
        remaining = sorted(tree.items(), key=lambda i: i.begin)
        self.assertEqual(len(remaining), 2)
        
        self.assertEqual(remaining[0].data, "side: left")
        self.assertEqual(remaining[1].data, "side: right")

    def test_slice_operation(self):
        """Test slicing intervals at a point."""
        tree = IntervalTree()
        tree.add(Interval(0.0, 10.0, "big"))
        tree.add(Interval(5.0, 15.0, "overlapping"))
        tree.add(Interval(20.0, 25.0, "separate"))
        
        # Slice at point 7
        tree.slice(7.0)
        
        # Should split the intervals that contain point 7
        intervals = sorted(tree.items(), key=lambda i: i.begin)
        
        # Should have: [0,7), [7,10), [5,7), [7,15), [20,25)
        # But [5,7) and [0,7) might overlap, and [7,10) and [7,15) start at same point
        self.assertGreater(len(intervals), 3)  # At least the separate interval plus splits
        
        # Check that no interval spans across point 7
        for interval in intervals:
            if interval.begin < 7.0:
                self.assertLessEqual(interval.end, 7.0)
            if interval.end > 7.0:
                self.assertGreaterEqual(interval.begin, 7.0)

    def test_slice_with_datafunc(self):
        """Test slicing with a data function."""
        tree = IntervalTree()
        tree.add(Interval(0.0, 10.0, "original"))
        
        def datafunc(interval, islower):
            return f"split: {'left' if islower else 'right'}"
        
        tree.slice(5.0, datafunc)
        
        intervals = sorted(tree.items(), key=lambda i: i.begin)
        self.assertEqual(len(intervals), 2)
        
        self.assertEqual(intervals[0].data, "split: left")
        self.assertEqual(intervals[1].data, "split: right")

    def test_copy_operation(self):
        """Test copying the tree."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 3.0, "a"))
        tree.add(Interval(4.0, 6.0, "b"))
        
        # Copy the tree
        tree_copy = tree.copy()
        
        # Should have same intervals
        self.assertEqual(len(tree), len(tree_copy))
        self.assertEqual(tree == tree_copy, True)
        
        # But should be different objects
        self.assertIsNot(tree, tree_copy)
        
        # Modifying copy shouldn't affect original
        tree_copy.add(Interval(10.0, 12.0, "c"))
        self.assertEqual(len(tree), 2)
        self.assertEqual(len(tree_copy), 3)

    def test_split_overlaps_operation(self):
        """Test splitting overlapping intervals."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 5.0, "A"))
        tree.add(Interval(3.0, 9.0, "C"))
        
        # Split overlaps
        tree.split_overlaps()


        # Should have more intervals now, split at boundary points
        intervals = sorted(tree.items(), key=lambda i: i.begin)
        self.assertEqual(len(intervals), 4)

    def test_merge_overlaps_operation(self):
        """Test merging overlapping intervals."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 3.0, "A"))
        tree.add(Interval(2.0, 4.0, "B"))
        tree.add(Interval(6.0, 8.0, "C"))
        
        original_count = len(tree)
        
        # Merge overlaps
        tree.merge_overlaps()
        
        # Should have fewer intervals
        self.assertLess(len(tree), original_count)
        
        # The overlapping intervals should be merged
        intervals = list(tree.items())
        # Should have 2 intervals: merged [1,4) and separate [6,8)
        self.assertEqual(len(intervals), 2)

    def test_merge_equals_operation(self):
        """Test merging intervals with identical ranges."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 3.0, "A"))
        tree.add(Interval(1.0, 3.0, "B"))
        tree.add(Interval(4.0, 6.0, "C"))
        
        # Merge equals
        tree.merge_equals()
        
        # Should have 2 intervals now
        intervals = list(tree.items())
        self.assertEqual(len(intervals), 2)

    def test_merge_neighbors_operation(self):
        """Test merging adjacent intervals."""
        tree = IntervalTree()
        tree.add(Interval(1.0, 3.0, "A"))
        tree.add(Interval(3.0, 5.0, "B"))  # Adjacent
        tree.add(Interval(7.0, 9.0, "C"))  # Separate
        
        # Merge neighbors
        tree.merge_neighbors()
        
        # Should have 2 intervals now: merged [1,5) and separate [7,9)
        intervals = sorted(tree.items(), key=lambda i: i.begin)
        self.assertEqual(len(intervals), 2)
        self.assertEqual(intervals[0].begin, 1.0)
        self.assertEqual(intervals[0].end, 5.0)
        self.assertEqual(intervals[1].begin, 7.0)
        self.assertEqual(intervals[1].end, 9.0)

    def test_inclusive(self):
        tree = IntervalTree(start_inclusive=True, end_inclusive=False)
        interval = Interval(1, 10, None, start_inclusive=True, end_inclusive=True)
        tree.add(interval)
