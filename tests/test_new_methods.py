"""Tests for newly added methods matching intervaltree API."""
import pytest
from manzanita import Interval, IntervalTree


class TestIntervalContainsPoint:
    def test_contains_point_inside(self):
        iv = Interval(1, 5, "data")
        assert iv.contains_point(3) is True

    def test_contains_point_at_begin(self):
        iv = Interval(1, 5, "data")
        assert iv.contains_point(1) is True  # start_inclusive=True by default

    def test_contains_point_at_end(self):
        iv = Interval(1, 5, "data")
        assert iv.contains_point(5) is False  # end_inclusive=False by default

    def test_contains_point_outside(self):
        iv = Interval(1, 5, "data")
        assert iv.contains_point(0) is False
        assert iv.contains_point(6) is False

    def test_contains_point_matches_overlaps(self):
        iv = Interval(1, 5, "data")
        for p in [0, 1, 2, 3, 4, 5, 6]:
            assert iv.contains_point(p) == iv.overlaps(p)


class TestIntervalContainsInterval:
    def test_contains_larger(self):
        iv = Interval(1, 10)
        other = Interval(3, 7)
        assert iv.contains_interval(other) is True

    def test_contains_same_range(self):
        iv = Interval(1, 5)
        other = Interval(1, 5, "different data")
        assert iv.contains_interval(other) is True

    def test_does_not_contain_wider(self):
        iv = Interval(3, 7)
        other = Interval(1, 10)
        assert iv.contains_interval(other) is False

    def test_does_not_contain_partial_overlap(self):
        iv = Interval(1, 5)
        other = Interval(3, 7)
        assert iv.contains_interval(other) is False

    def test_does_not_contain_disjoint(self):
        iv = Interval(1, 3)
        other = Interval(5, 7)
        assert iv.contains_interval(other) is False


class TestIntervalDistanceTo:
    def test_distance_to_point_inside(self):
        iv = Interval(1, 5)
        assert iv.distance_to(3.0) == 0.0

    def test_distance_to_point_before(self):
        iv = Interval(3, 7)
        assert iv.distance_to(1.0) == 2.0

    def test_distance_to_point_after(self):
        iv = Interval(1, 5)
        assert iv.distance_to(8.0) == 3.0

    def test_distance_to_overlapping_interval(self):
        iv = Interval(1, 5)
        other = Interval(3, 7)
        assert iv.distance_to(other) == 0.0

    def test_distance_to_disjoint_interval_after(self):
        iv = Interval(1, 3)
        other = Interval(5, 7)
        assert iv.distance_to(other) == 2.0

    def test_distance_to_disjoint_interval_before(self):
        iv = Interval(5, 7)
        other = Interval(1, 3)
        assert iv.distance_to(other) == 2.0

    def test_distance_to_adjacent_intervals(self):
        iv = Interval(1, 3)
        other = Interval(3, 5)
        # [1, 3) and [3, 5) don't overlap (3 is exclusive in first)
        assert iv.distance_to(other) == 0.0  # gap is 3 - 3 = 0

    def test_distance_to_invalid_type(self):
        iv = Interval(1, 5)
        with pytest.raises(TypeError):
            iv.distance_to("not a number")


class TestIntervalOverlapSize:
    def test_overlap_size_full_overlap(self):
        iv = Interval(1, 5)
        assert iv.overlap_size(1, 5) == 4.0

    def test_overlap_size_partial_overlap(self):
        iv = Interval(1, 5)
        assert iv.overlap_size(3, 7) == 2.0

    def test_overlap_size_no_overlap(self):
        iv = Interval(1, 3)
        assert iv.overlap_size(5, 7) == 0.0

    def test_overlap_size_contained(self):
        iv = Interval(1, 10)
        assert iv.overlap_size(3, 7) == 4.0

    def test_overlap_size_point_contained(self):
        iv = Interval(1, 5)
        assert iv.overlap_size(3) == 1.0

    def test_overlap_size_point_not_contained(self):
        iv = Interval(1, 5)
        assert iv.overlap_size(6) == 0.0


class TestIntervalRangeMatches:
    def test_same_range_different_data(self):
        iv1 = Interval(1, 5, "a")
        iv2 = Interval(1, 5, "b")
        assert iv1.range_matches(iv2) is True

    def test_same_range_same_data(self):
        iv1 = Interval(1, 5, "a")
        iv2 = Interval(1, 5, "a")
        assert iv1.range_matches(iv2) is True

    def test_different_range(self):
        iv1 = Interval(1, 5)
        iv2 = Interval(1, 6)
        assert iv1.range_matches(iv2) is False

    def test_completely_different(self):
        iv1 = Interval(1, 3)
        iv2 = Interval(5, 7)
        assert iv1.range_matches(iv2) is False


class TestIntervalCopy:
    def test_copy_creates_equal_interval(self):
        iv = Interval(1, 5, "data")
        iv_copy = iv.copy()
        assert iv == iv_copy
        assert iv.begin == iv_copy.begin
        assert iv.end == iv_copy.end
        assert iv.data == iv_copy.data

    def test_copy_independence(self):
        iv = Interval(1, 5, [1, 2, 3])
        iv_copy = iv.copy()
        assert iv == iv_copy


class TestTreeAppend:
    def test_append_new_interval(self):
        tree = IntervalTree()
        tree.append(Interval(1, 3, "a"))
        assert len(tree) == 1

    def test_append_duplicate_does_nothing(self):
        tree = IntervalTree()
        iv = Interval(1, 3, "a")
        tree.append(iv)
        tree.append(Interval(1, 3, "a"))
        assert len(tree) == 1

    def test_append_different_data(self):
        tree = IntervalTree()
        tree.append(Interval(1, 3, "a"))
        tree.append(Interval(1, 3, "b"))
        assert len(tree) == 2

    def test_appendi(self):
        tree = IntervalTree()
        tree.appendi(1, 3, "a")
        tree.appendi(1, 3, "a")
        assert len(tree) == 1

    def test_appendi_different_data(self):
        tree = IntervalTree()
        tree.appendi(1, 3, "a")
        tree.appendi(1, 3, "b")
        assert len(tree) == 2


class TestTreeRange:
    def test_range_basic(self):
        tree = IntervalTree()
        tree.addi(1, 5)
        tree.addi(3, 7)
        r = tree.range()
        assert r.begin == 1.0
        assert r.end == 7.0

    def test_range_empty_tree(self):
        tree = IntervalTree()
        assert tree.range() is None

    def test_range_single_interval(self):
        tree = IntervalTree()
        tree.addi(2, 8)
        r = tree.range()
        assert r.begin == 2.0
        assert r.end == 8.0

    def test_range_non_overlapping(self):
        tree = IntervalTree()
        tree.addi(1, 3)
        tree.addi(5, 7)
        tree.addi(10, 15)
        r = tree.range()
        assert r.begin == 1.0
        assert r.end == 15.0

    def test_range_wide_interval_early(self):
        """Test that range uses max_end, not the end of the rightmost-begin interval."""
        tree = IntervalTree()
        tree.addi(1, 100)  # Starts early but has the max end
        tree.addi(50, 60)  # Starts later but ends earlier
        r = tree.range()
        assert r.begin == 1.0
        assert r.end == 100.0


class TestTreeSpan:
    def test_span_basic(self):
        tree = IntervalTree()
        tree.addi(1, 5)
        tree.addi(3, 7)
        assert tree.span() == 6.0

    def test_span_empty_tree(self):
        tree = IntervalTree()
        assert tree.span() == 0.0

    def test_span_single_interval(self):
        tree = IntervalTree()
        tree.addi(2, 8)
        assert tree.span() == 6.0

    def test_span_wide_interval_early(self):
        tree = IntervalTree()
        tree.addi(1, 100)
        tree.addi(50, 60)
        assert tree.span() == 99.0


class TestTreeIsdisjoint:
    def test_disjoint_trees(self):
        t1 = IntervalTree()
        t1.addi(1, 3, "a")
        t2 = IntervalTree()
        t2.addi(5, 7, "b")
        assert t1.isdisjoint(t2) is True

    def test_non_disjoint_trees(self):
        t1 = IntervalTree()
        t1.addi(1, 3, "a")
        t2 = IntervalTree()
        t2.addi(1, 3, "a")
        assert t1.isdisjoint(t2) is False

    def test_overlapping_ranges_but_disjoint_sets(self):
        """Trees with geometrically overlapping intervals but no identical intervals."""
        t1 = IntervalTree()
        t1.addi(1, 5, "a")
        t2 = IntervalTree()
        t2.addi(3, 7, "b")
        assert t1.isdisjoint(t2) is True

    def test_empty_trees(self):
        t1 = IntervalTree()
        t2 = IntervalTree()
        assert t1.isdisjoint(t2) is True

    def test_one_empty_tree(self):
        t1 = IntervalTree()
        t1.addi(1, 3)
        t2 = IntervalTree()
        assert t1.isdisjoint(t2) is True


class TestTreeFindNested:
    def test_find_nested_basic(self):
        tree = IntervalTree()
        tree.addi(1, 10, "parent")
        tree.addi(3, 5, "child")
        nested = tree.find_nested()
        assert len(nested) == 1
        # The parent interval should map to a set containing the child
        for parent, children in nested.items():
            assert parent.begin == 1.0
            assert parent.end == 10.0
            assert len(children) == 1
            child = list(children)[0]
            assert child.begin == 3.0
            assert child.end == 5.0

    def test_find_nested_no_nesting(self):
        tree = IntervalTree()
        tree.addi(1, 3)
        tree.addi(5, 7)
        nested = tree.find_nested()
        assert len(nested) == 0

    def test_find_nested_empty_tree(self):
        tree = IntervalTree()
        nested = tree.find_nested()
        assert len(nested) == 0

    def test_find_nested_multiple_children(self):
        tree = IntervalTree()
        tree.addi(1, 20, "parent")
        tree.addi(3, 5, "child1")
        tree.addi(7, 10, "child2")
        tree.addi(12, 15, "child3")
        nested = tree.find_nested()
        assert len(nested) == 1
        for parent, children in nested.items():
            assert parent.begin == 1.0
            assert len(children) == 3

    def test_find_nested_multiple_levels(self):
        tree = IntervalTree()
        tree.addi(1, 20, "grandparent")
        tree.addi(3, 15, "parent")
        tree.addi(5, 10, "child")
        nested = tree.find_nested()
        # Grandparent contains parent and child
        # Parent contains child
        assert len(nested) == 2


class TestTreePrintStructure:
    def test_print_structure_tostring(self):
        tree = IntervalTree()
        tree.addi(1, 5, "a")
        tree.addi(3, 7, "b")
        result = tree.print_structure(tostring=True)
        assert isinstance(result, str)
        assert "1" in result
        assert "5" in result

    def test_print_structure_empty(self):
        tree = IntervalTree()
        result = tree.print_structure(tostring=True)
        assert result == "<empty IntervalTree>"

    def test_print_structure_default_prints(self, capsys):
        tree = IntervalTree()
        tree.addi(1, 5, "a")
        result = tree.print_structure()
        assert result is None
        captured = capsys.readouterr()
        assert "1" in captured.out
