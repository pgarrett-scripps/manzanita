#!/usr/bin/env python3
"""
Test script for the new boundary inclusivity features in Manzanita.
"""

import sys
import os

# Add the target directory to Python path to import the compiled module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'target/release'))

try:
    from manzanita import Interval, IntervalTree, BoundaryType
    print("✓ Successfully imported manzanita with new boundary features")
except ImportError as e:
    print(f"✗ Failed to import manzanita: {e}")
    sys.exit(1)

def test_default_behavior():
    """Test that default behavior is [start_inclusive=True, end_inclusive=False]"""
    print("\n=== Testing Default Behavior ===")
    
    # Default interval should be [1.0, 5.0) - inclusive start, exclusive end
    interval = Interval(1.0, 5.0, "test")
    
    print(f"Interval: {interval}")
    print(f"start_inclusive: {interval.start_inclusive}")
    print(f"end_inclusive: {interval.end_inclusive}")
    
    # Test point overlaps
    assert interval.overlaps(1.0) == True, "Start point should be included (inclusive)"
    assert interval.overlaps(3.0) == True, "Middle point should be included"
    assert interval.overlaps(5.0) == False, "End point should be excluded (exclusive)"
    
    print("✓ Default behavior working correctly: [start_inclusive=True, end_inclusive=False]")

def test_custom_boundaries():
    """Test custom boundary configurations"""
    print("\n=== Testing Custom Boundaries ===")
    
    # Test all inclusive [1.0, 5.0]
    interval_inclusive = Interval(1.0, 5.0, "inclusive", start_inclusive=True, end_inclusive=True)
    print(f"All inclusive interval: {interval_inclusive}")
    assert interval_inclusive.overlaps(1.0) == True, "Start should be included"
    assert interval_inclusive.overlaps(5.0) == True, "End should be included"
    
    # Test all exclusive (1.0, 5.0)
    interval_exclusive = Interval(1.0, 5.0, "exclusive", start_inclusive=False, end_inclusive=False)
    print(f"All exclusive interval: {interval_exclusive}")
    assert interval_exclusive.overlaps(1.0) == False, "Start should be excluded"
    assert interval_exclusive.overlaps(5.0) == False, "End should be excluded"
    assert interval_exclusive.overlaps(3.0) == True, "Middle should be included"
    
    # Test opposite of default: (1.0, 5.0] - exclusive start, inclusive end
    interval_opposite = Interval(1.0, 5.0, "opposite", start_inclusive=False, end_inclusive=True)
    print(f"Opposite interval: {interval_opposite}")
    assert interval_opposite.overlaps(1.0) == False, "Start should be excluded"
    assert interval_opposite.overlaps(5.0) == True, "End should be included"
    
    print("✓ Custom boundary configurations working correctly")

def test_tree_with_boundaries():
    """Test IntervalTree with custom boundary defaults"""
    print("\n=== Testing IntervalTree with Custom Boundaries ===")
    
    # Create tree with all-inclusive boundaries by default
    tree_inclusive = IntervalTree(start_inclusive=True, end_inclusive=True)
    print(f"Tree with inclusive boundaries: start={tree_inclusive.start_inclusive}, end={tree_inclusive.end_inclusive}")
    
    # Create tree with all-exclusive boundaries by default
    tree_exclusive = IntervalTree(start_inclusive=False, end_inclusive=False)
    print(f"Tree with exclusive boundaries: start={tree_exclusive.start_inclusive}, end={tree_exclusive.end_inclusive}")
    
    print("✓ IntervalTree boundary configuration working correctly")

def test_from_tuples_with_boundaries():
    """Test creating tree from tuples with custom boundaries"""
    print("\n=== Testing from_tuples with Custom Boundaries ===")
    
    # Create tree from tuples with inclusive end boundaries
    tuples = [(1.0, 3.0), (2.0, 4.0, "data"), (5.0, 7.0)]
    tree = IntervalTree.from_tuples(tuples, start_inclusive=True, end_inclusive=True)
    
    print(f"Tree created from tuples with inclusive boundaries")
    print(f"Tree boundaries: start={tree.start_inclusive}, end={tree.end_inclusive}")
    
    # Check that intervals in the tree have the correct boundaries
    for interval in tree:
        print(f"  {interval}")
        assert interval.start_inclusive == True, "All intervals should have inclusive start"
        assert interval.end_inclusive == True, "All intervals should have inclusive end"
    
    print("✓ from_tuples with custom boundaries working correctly")

if __name__ == "__main__":
    print("Testing Manzanita Boundary Inclusivity Features")
    print("=" * 50)
    
    try:
        test_default_behavior()
        test_custom_boundaries()
        test_tree_with_boundaries()
        test_from_tuples_with_boundaries()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Boundary inclusivity feature is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
