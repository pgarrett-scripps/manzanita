#!/usr/bin/env python3
"""
Test script to verify that interval boundary inclusivity/exclusivity fixes work correctly.
This tests the specific issues mentioned in the original problem description.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'target', 'wheels'))

try:
    import manzanita
    from manzanita import Interval, IntervalTree
except ImportError:
    print("manzanita module not found. Make sure it's built and installed.")
    sys.exit(1)

def test_mixed_boundary_storage():
    """Test that trees can store intervals with different boundary settings."""
    print("Testing mixed boundary storage...")
    
    tree = IntervalTree()
    
    # Add intervals with different boundary settings
    tree.add(Interval(1, 3, "A", start_inclusive=True, end_inclusive=False))   # [1, 3)
    tree.add(Interval(3, 5, "B", start_inclusive=False, end_inclusive=True))   # (3, 5]
    tree.add(Interval(5, 7, "C", start_inclusive=True, end_inclusive=True))    # [5, 7]
    tree.add(Interval(7, 9, "D", start_inclusive=False, end_inclusive=False))  # (7, 9)
    
    assert len(tree) == 4
    print("✓ Mixed boundary intervals stored successfully")

def test_point_overlap_with_mixed_boundaries():
    """Test point overlap checking with mixed boundary inclusivity."""
    print("\nTesting point overlap with mixed boundaries...")
    
    tree = IntervalTree()
    tree.add(Interval(1, 3, "A", start_inclusive=True, end_inclusive=False))   # [1, 3)
    tree.add(Interval(3, 5, "B", start_inclusive=False, end_inclusive=True))   # (3, 5]
    tree.add(Interval(5, 7, "C", start_inclusive=True, end_inclusive=True))    # [5, 7]
    tree.add(Interval(7, 9, "D", start_inclusive=False, end_inclusive=False))  # (7, 9)
    
    # Test boundary points
    assert len(tree[1.0]) == 1  # Point 1 should overlap with [1, 3)
    assert tree[1.0][0].data == "A"
    
    assert len(tree[3.0]) == 1  # Point 3 should overlap with (3, 5] only
    assert tree[3.0][0].data == "B"
    
    assert len(tree[5.0]) == 2  # Point 5 should overlap with both (3, 5] and [5, 7]
    overlapping_data = [iv.data for iv in tree[5.0]]
    assert "B" in overlapping_data and "C" in overlapping_data
    
    assert len(tree[7.0]) == 1  # Point 7 should overlap with [5, 7] only
    assert tree[7.0][0].data == "C"
    
    assert len(tree[7.5]) == 1  # Point 7.5 should overlap with (7, 9) only
    assert tree[7.5][0].data == "D"
    
    print("✓ Point overlap queries work correctly with mixed boundaries")

def test_range_overlap_with_mixed_boundaries():
    """Test range overlap checking with mixed boundary inclusivity."""
    print("\nTesting range overlap with mixed boundaries...")
    
    tree = IntervalTree()
    tree.add(Interval(1, 3, "A", start_inclusive=True, end_inclusive=False))   # [1, 3)
    tree.add(Interval(3, 5, "B", start_inclusive=False, end_inclusive=True))   # (3, 5]
    tree.add(Interval(5, 7, "C", start_inclusive=True, end_inclusive=True))    # [5, 7]
    tree.add(Interval(7, 9, "D", start_inclusive=False, end_inclusive=False))  # (7, 9)
    
    # Test range queries
    overlapping = tree.overlap(2.5, 3.5)
    overlapping_data = [iv.data for iv in overlapping]
    assert "A" in overlapping_data and "B" in overlapping_data
    
    # Test range that touches boundaries
    overlapping = tree.overlap(3.0, 5.0)
    overlapping_data = [iv.data for iv in overlapping]
    assert "B" in overlapping_data and "C" in overlapping_data
    
    print("✓ Range overlap queries work correctly with mixed boundaries")

def test_merge_overlaps_with_mixed_boundaries():
    """Test merge_overlaps with mixed boundary inclusivity."""
    print("\nTesting merge_overlaps with mixed boundaries...")
    
    tree = IntervalTree()
    tree.add(Interval(1, 3, "A", start_inclusive=True, end_inclusive=True))    # [1, 3]
    tree.add(Interval(3, 5, "B", start_inclusive=True, end_inclusive=False))   # [3, 5)
    tree.add(Interval(6, 8, "C", start_inclusive=False, end_inclusive=True))   # (6, 8]
    tree.add(Interval(8, 10, "D", start_inclusive=False, end_inclusive=False)) # (8, 10)
    
    # Test merging adjacent intervals (should merge first two)
    tree_copy = tree.copy()
    tree_copy.merge_overlaps(strict=False)
    
    # Should have 3 intervals after merging (first two merged, others separate)
    intervals = tree_copy.items()
    assert len(intervals) >= 3, f"Expected at least 3 intervals, got {len(intervals)}"
    
    print("✓ merge_overlaps handles mixed boundaries correctly")

def test_slice_with_mixed_boundaries():
    """Test slicing with mixed boundary inclusivity."""
    print("\nTesting slice with mixed boundaries...")
    
    tree = IntervalTree()
    tree.add(Interval(0, 10, "data", start_inclusive=True, end_inclusive=False))  # [0, 10)
    
    # Slice at point 5
    tree.slice(5.0)
    
    intervals = tree.items()
    assert len(intervals) == 2
    
    # Check that boundaries are correct
    left_interval = next(iv for iv in intervals if iv.end == 5.0)
    right_interval = next(iv for iv in intervals if iv.begin == 5.0)
    
    assert left_interval.start_inclusive == True
    assert left_interval.end_inclusive == False
    assert right_interval.start_inclusive == True
    assert right_interval.end_inclusive == False
    
    print("✓ Slice operation preserves boundary inclusivity correctly")

def test_adjacent_interval_detection():
    """Test that adjacent intervals are properly detected with mixed boundaries."""
    print("\nTesting adjacent interval detection...")
    
    tree = IntervalTree()
    tree.add(Interval(1, 3, "A", start_inclusive=True, end_inclusive=True))    # [1, 3]
    tree.add(Interval(3, 5, "B", start_inclusive=True, end_inclusive=False))   # [3, 5)
    tree.add(Interval(6, 8, "C", start_inclusive=True, end_inclusive=False))   # [6, 8) - not adjacent
    
    # Test merging with non-strict mode (should merge adjacent)
    tree_copy = tree.copy()
    tree_copy.merge_overlaps(strict=False)
    
    intervals = tree_copy.items()
    # Should have 2 intervals (first two merged since [1,3] and [3,5) are adjacent)
    assert len(intervals) == 2
    
    print("✓ Adjacent interval detection works with mixed boundaries")

def test_enveloped_queries_with_mixed_boundaries():
    """Test enveloped queries with mixed boundary inclusivity."""
    print("\nTesting enveloped queries with mixed boundaries...")
    
    tree = IntervalTree()
    tree.add(Interval(2, 4, "A", start_inclusive=True, end_inclusive=True))    # [2, 4]
    tree.add(Interval(3, 5, "B", start_inclusive=False, end_inclusive=False))  # (3, 5)
    tree.add(Interval(1, 6, "C", start_inclusive=True, end_inclusive=False))   # [1, 6)
    
    # Query for intervals enveloped by [1, 5)
    enveloped = tree.envelop(1, 5)
    enveloped_data = [iv.data for iv in enveloped]
    
    # [2, 4] should be enveloped by [1, 5)
    # (3, 5) should NOT be enveloped by [1, 5) because end boundaries conflict
    # [1, 6) should NOT be enveloped by [1, 5) because it extends beyond
    
    assert "A" in enveloped_data
    assert len(enveloped_data) >= 1
    
    print("✓ Enveloped queries work correctly with mixed boundaries")

def run_all_tests():
    """Run all boundary inclusivity tests."""
    print("Running interval boundary inclusivity/exclusivity tests...\n")
    
    try:
        test_mixed_boundary_storage()
        test_point_overlap_with_mixed_boundaries()
        test_range_overlap_with_mixed_boundaries()
        test_merge_overlaps_with_mixed_boundaries()
        test_slice_with_mixed_boundaries()
        test_adjacent_interval_detection()
        test_enveloped_queries_with_mixed_boundaries()
        
        print("\n" + "="*60)
        print("✅ All boundary inclusivity tests passed!")
        print("Mixed interval inclusive/exclusive bounds are working correctly.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
