# Ported from intervaltree test/intervaltree_methods/debug_test.py
"""
Test module: IntervalTree, Debug/analysis methods (print_structure, verify, score)
"""
from manzanita import Interval, IntervalTree
import pytest
from tests.intervaltree_compat import data
from tests.intervaltree_compat.conftest import make_tree_deduped


def test_print_empty():
    t = IntervalTree()
    assert t.print_structure(tostring=True) == "<empty IntervalTree>"
    t.print_structure()
    t.verify()


def test_print_nonempty():
    t = make_tree_deduped(data.ivs1.data)
    s = t.print_structure(tostring=True)
    assert isinstance(s, str)
    assert len(s) > 0
    assert "Node:" in s
    t.verify()


def test_small_tree_score():
    t = IntervalTree()
    assert t.score() == 0.0

    t.addi(1, 4)
    assert t.score() == 0.0

    t.addi(2, 5)
    assert t.score() == 0.0


def test_score_no_report():
    t = make_tree_deduped(data.ivs1.data)
    score = t.score(False)
    assert isinstance(score, (int, float))


def test_score_full_report():
    t = make_tree_deduped(data.ivs1.data)
    report = t.score(full_report=True)
    assert isinstance(report, dict)
    assert 'depth' in report
    assert 's_center' in report
    assert '_cumulative' in report


def test_verify_empty():
    t = IntervalTree()
    t.verify()


def test_verify_nonempty():
    t = make_tree_deduped(data.ivs1.data)
    t.verify()


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
