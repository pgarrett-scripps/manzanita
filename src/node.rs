//! Internal node structure for the interval tree.
//!
//! This module provides the `IntervalNode` implementation which forms the building blocks
//! of the interval tree data structure. Each node maintains an interval and the maximum
//! end value of its subtree for efficient search pruning.

use crate::interval::Interval;
use pyo3::prelude::*;
use std::sync::Arc;

/// Node structure for an Interval Tree node.
///
/// Each node contains an interval and maintains the maximum end value
/// of all intervals in its subtree for efficient pruning during searches.
#[derive(Clone)]
pub(crate) struct IntervalNode {
    pub interval: Arc<Interval>,
    pub max_end: f64,
    pub left: Option<Box<IntervalNode>>,
    pub right: Option<Box<IntervalNode>>,
}

impl IntervalNode {
    /// Creates a new IntervalNode with the given interval.
    pub fn new(interval: Arc<Interval>) -> Self {
        let max_end = interval.end;
        IntervalNode {
            interval,
            max_end,
            left: None,
            right: None,
        }
    }

    /// Inserts a new interval into the tree using BST ordering on begin values.
    pub fn insert(&mut self, interval: Arc<Interval>) {
        // Add safety check to prevent infinite recursion with NaN values
        if interval.begin.is_nan() || interval.end.is_nan() {
            return;
        }

        // Use a more robust comparison to handle floating point edge cases
        if interval.begin < self.interval.begin
            || (interval.begin == self.interval.begin && interval.end < self.interval.end)
        {
            match &mut self.left {
                Some(left) => left.insert(interval),
                None => self.left = Some(Box::new(IntervalNode::new(interval))),
            }
        } else {
            match &mut self.right {
                Some(right) => right.insert(interval),
                None => self.right = Some(Box::new(IntervalNode::new(interval))),
            }
        }
        self.update_max_end();
    }

    /// Updates the max_end value based on the current node and its children.
    /// This optimization allows for efficient search pruning.
    pub fn update_max_end(&mut self) {
        self.max_end = self.interval.end;

        if let Some(ref left) = self.left {
            if left.max_end.is_finite() && left.max_end > self.max_end {
                self.max_end = left.max_end;
            }
        }

        if let Some(ref right) = self.right {
            if right.max_end.is_finite() && right.max_end > self.max_end {
                self.max_end = right.max_end;
            }
        }
    }

    /// Searches for all intervals overlapping with a given point.
    /// Uses max_end values for efficient pruning.
    pub fn search_point(&self, point: f64, result: &mut Vec<Arc<Interval>>) {
        if self.interval.overlaps(point) {
            result.push(self.interval.clone());
        }

        // Search left subtree if it might contain overlapping intervals
        if let Some(ref left) = self.left {
            // An interval in the left subtree can contain the point if:
            // 1. Its end > point (strict inequality), OR
            // 2. Its end == point AND it has inclusive end boundary
            // Since we don't track individual boundary types in max_end, we must be conservative
            if left.max_end > point || (left.max_end == point && left.could_have_inclusive_end()) {
                left.search_point(point, result);
            }
        }

        // Search right subtree if the point could overlap with intervals starting at or after this node's begin
        if let Some(ref right) = self.right {
            // An interval in the right subtree can contain the point if:
            // 1. Its begin < point (since we know point >= self.interval.begin from BST property), OR
            // 2. Its begin == point AND it has inclusive start boundary
            if point > self.interval.begin
                || (point == self.interval.begin && self.interval.start_inclusive)
            {
                right.search_point(point, result);
            }
        }
    }

    /// Helper method to check if this subtree could have intervals with inclusive end boundaries
    fn could_have_inclusive_end(&self) -> bool {
        // Check this node's interval
        if self.interval.end_inclusive {
            return true;
        }

        // Recursively check children
        if let Some(ref left) = self.left {
            if left.could_have_inclusive_end() {
                return true;
            }
        }

        if let Some(ref right) = self.right {
            if right.could_have_inclusive_end() {
                return true;
            }
        }

        false
    }

    /// Searches for all intervals overlapping with a given range [start, end).
    /// Note: The search range is assumed to be [start, end) (start inclusive, end exclusive)
    /// unless specified otherwise.
    pub fn search_range(&self, start: f64, end: f64, result: &mut Vec<Arc<Interval>>) {
        if self.interval.overlaps_range(start, end) {
            result.push(self.interval.clone());
        }

        // Search left subtree if it might contain overlapping intervals
        if let Some(ref left) = self.left {
            // An interval in the left subtree can overlap [start, end) if its end > start
            // OR if its end == start and it has inclusive end boundary
            if left.max_end > start || (left.max_end == start && left.could_have_inclusive_end()) {
                left.search_range(start, end, result);
            }
        }

        // Search right subtree if intervals starting at or after this node could overlap the range
        if let Some(ref right) = self.right {
            // An interval in the right subtree can overlap [start, end) if its begin < end
            // Since all intervals in right subtree have begin >= self.interval.begin,
            // we only need to check if self.interval.begin < end
            if self.interval.begin < end {
                right.search_range(start, end, result);
            }
        }
    }

    /// In-order traversal to collect all intervals in the tree.
    pub fn collect_intervals(&self, result: &mut Vec<Arc<Interval>>) {
        if let Some(ref left) = self.left {
            left.collect_intervals(result);
        }
        result.push(self.interval.clone());
        if let Some(ref right) = self.right {
            right.collect_intervals(result);
        }
    }

    /// Efficiently counts the number of intervals in the tree.
    pub fn count_intervals(&self) -> usize {
        1 + self.left.as_ref().map_or(0, |node| node.count_intervals())
            + self.right.as_ref().map_or(0, |node| node.count_intervals())
    }

    /// Counts the total number of nodes in the subtree rooted at this node
    pub fn count_nodes(&self) -> usize {
        let mut count = 1; // Count this node

        if let Some(ref left) = self.left {
            count += left.count_nodes();
        }

        if let Some(ref right) = self.right {
            count += right.count_nodes();
        }

        count
    }

    /// Calculates the depth score for tree optimality analysis
    ///
    /// Returns a normalized score indicating how balanced the tree is.
    /// A perfectly balanced tree returns 0.0, while a degenerate tree returns 1.0.
    pub fn depth_score(&self, n: usize, _m: usize) -> f64 {
        if n <= 1 {
            return 0.0;
        }

        let actual_depth = self.max_depth();
        let optimal_depth = (n as f64).log2().ceil() as usize;
        let worst_depth = n; // Completely degenerate tree

        if worst_depth <= optimal_depth {
            return 0.0;
        }

        let raw_score = actual_depth.saturating_sub(optimal_depth);
        let max_possible = worst_depth.saturating_sub(optimal_depth);

        if max_possible == 0 {
            0.0
        } else {
            (raw_score as f64) / (max_possible as f64)
        }
    }

    /// Calculates the maximum depth of the subtree rooted at this node
    fn max_depth(&self) -> usize {
        let left_depth = self.left.as_ref().map_or(0, |node| node.max_depth());
        let right_depth = self.right.as_ref().map_or(0, |node| node.max_depth());

        1 + left_depth.max(right_depth)
    }

    /// Helper to check if two intervals have equal data (Python object comparison is complex)
    pub fn interval_data_equals(&self, a: &Arc<Interval>, b: &Arc<Interval>) -> bool {
        Python::with_gil(|py| {
            match (
                a.data.as_ref(py).is(b.data.as_ref(py)),
                a.data.as_ref(py).eq(b.data.as_ref(py)),
            ) {
                (true, _) => true,         // Same object
                (false, Ok(true)) => true, // Equal content
                _ => false,                // Different or comparison failed
            }
        })
    }

    /// Search for intervals that are enveloped by a range [start, end)
    /// Note: The enveloping range is assumed to be [start, end) unless specified otherwise
    pub fn search_enveloped(&self, start: f64, end: f64, result: &mut Vec<Arc<Interval>>) {
        // An interval is enveloped by [start, end) if:
        // - interval.begin >= start (respecting start boundary inclusivity)
        // - interval.end <= end (respecting end boundary exclusivity)
        // But we need to be careful about the interval's own boundary inclusivity
        if self.interval.enveloped_by(start, end) {
            result.push(self.interval.clone());
        }

        // Search left subtree if it might contain enveloped intervals
        if let Some(ref left) = self.left {
            // Left subtree intervals can be enveloped if their max_end <= end
            if left.max_end <= end {
                left.search_enveloped(start, end, result);
            } else if left.max_end > start {
                // Even if max_end > end, some intervals might still be enveloped
                left.search_enveloped(start, end, result);
            }
        }

        // Search right subtree if it might contain enveloped intervals
        if let Some(ref right) = self.right {
            // Right subtree intervals can be enveloped if their begins are >= start
            // Since all right subtree intervals have begin >= self.interval.begin,
            // we need self.interval.begin >= start for any to be enveloped
            if self.interval.begin >= start {
                right.search_enveloped(start, end, result);
            }
        }
    }

    /// Check if a specific interval exists in the tree
    pub fn contains(&self, target: &Interval) -> bool {
        if self.interval.begin == target.begin
            && self.interval.end == target.end
            && self.interval_data_equals(&self.interval, &Arc::new(target.clone()))
        {
            true
        } else if target.begin < self.interval.begin {
            self.left.as_ref().is_some_and(|left| left.contains(target))
        } else {
            self.right
                .as_ref()
                .is_some_and(|right| right.contains(target))
        }
    }

    /// Find the leftmost interval
    pub fn find_leftmost(&self) -> &Arc<Interval> {
        if let Some(ref left) = self.left {
            left.find_leftmost()
        } else {
            &self.interval
        }
    }

    /// Find the rightmost interval  
    pub fn find_rightmost(&self) -> &Arc<Interval> {
        if let Some(ref right) = self.right {
            right.find_rightmost()
        } else {
            &self.interval
        }
    }

    /// Removes a specific interval from the tree
    pub fn remove(self: Box<Self>, target: &Interval) -> Option<Box<IntervalNode>> {
        let mut boxed_self = self;

        if boxed_self.interval.begin == target.begin
            && boxed_self.interval.end == target.end
            && boxed_self.interval_data_equals(&boxed_self.interval, &Arc::new(target.clone()))
        {
            // This is the node to remove
            match (boxed_self.left.take(), boxed_self.right.take()) {
                (None, None) => None,               // Leaf node, remove it
                (Some(left), None) => Some(left),   // Only left child
                (None, Some(right)) => Some(right), // Only right child
                (Some(left), Some(mut right)) => {
                    // Both children exist, replace with successor
                    let successor = right.extract_min();
                    boxed_self.interval = successor.interval;
                    boxed_self.left = Some(left);
                    boxed_self.right = Some(right);
                    boxed_self.update_max_end();
                    Some(boxed_self)
                }
            }
        } else if target.begin < boxed_self.interval.begin {
            if let Some(left) = boxed_self.left.take() {
                boxed_self.left = left.remove(target);
            }
            boxed_self.update_max_end();
            Some(boxed_self)
        } else {
            if let Some(right) = boxed_self.right.take() {
                boxed_self.right = right.remove(target);
            }
            boxed_self.update_max_end();
            Some(boxed_self)
        }
    }

    /// Extract and return the minimum node, removing it from the tree
    fn extract_min(&mut self) -> IntervalNode {
        if self.left.is_none() {
            IntervalNode {
                interval: self.interval.clone(),
                max_end: self.max_end,
                left: None,
                right: self.right.take(),
            }
        } else {
            let min_node = self.left.as_mut().unwrap().extract_min();
            self.update_max_end();
            min_node
        }
    }

    /// Remove all intervals that overlap with a point
    pub fn remove_overlap_point(self: Box<Self>, point: f64) -> Option<Box<IntervalNode>> {
        let mut to_remove = Vec::new();
        self.collect_overlapping_point(point, &mut to_remove);

        let mut result = Some(self);
        for interval in to_remove {
            if let Some(node) = result {
                result = node.remove(&interval);
            }
        }
        result
    }

    /// Remove all intervals that overlap with a range
    pub fn remove_overlap_range(
        self: Box<Self>,
        start: f64,
        end: f64,
    ) -> Option<Box<IntervalNode>> {
        let mut to_remove = Vec::new();
        self.collect_overlapping_range(start, end, &mut to_remove);

        let mut result = Some(self);
        for interval in to_remove {
            if let Some(node) = result {
                result = node.remove(&interval);
            }
        }
        result
    }

    /// Remove all intervals that are enveloped by a range
    pub fn remove_enveloped(self: Box<Self>, start: f64, end: f64) -> Option<Box<IntervalNode>> {
        let mut to_remove = Vec::new();
        self.collect_enveloped(start, end, &mut to_remove);

        let mut result = Some(self);
        for interval in to_remove {
            if let Some(node) = result {
                result = node.remove(&interval);
            }
        }
        result
    }

    /// Helper to collect intervals overlapping with a point
    fn collect_overlapping_point(&self, point: f64, result: &mut Vec<Arc<Interval>>) {
        if self.interval.overlaps(point) {
            result.push(self.interval.clone());
        }

        if let Some(ref left) = self.left {
            if left.max_end > point || (left.max_end == point && left.could_have_inclusive_end()) {
                left.collect_overlapping_point(point, result);
            }
        }

        if let Some(ref right) = self.right {
            if point > self.interval.begin
                || (point == self.interval.begin && self.interval.start_inclusive)
            {
                right.collect_overlapping_point(point, result);
            }
        }
    }

    /// Helper to collect intervals overlapping with a range
    fn collect_overlapping_range(&self, start: f64, end: f64, result: &mut Vec<Arc<Interval>>) {
        if self.interval.overlaps_range(start, end) {
            result.push(self.interval.clone());
        }

        if let Some(ref left) = self.left {
            if left.max_end > start || (left.max_end == start && left.could_have_inclusive_end()) {
                left.collect_overlapping_range(start, end, result);
            }
        }

        if let Some(ref right) = self.right {
            if self.interval.begin < end {
                right.collect_overlapping_range(start, end, result);
            }
        }
    }

    /// Helper to collect intervals enveloped by a range
    fn collect_enveloped(&self, start: f64, end: f64, result: &mut Vec<Arc<Interval>>) {
        if self.interval.enveloped_by(start, end) {
            result.push(self.interval.clone());
        }

        if let Some(ref left) = self.left {
            if left.max_end > start {
                left.collect_enveloped(start, end, result);
            }
        }

        if let Some(ref right) = self.right {
            if self.interval.begin < end {
                right.collect_enveloped(start, end, result);
            }
        }
    }

    /// Verifies that this node and its subtree maintain interval tree invariants
    ///
    /// This is used internally by the tree's verify() method for debugging.
    pub fn verify_subtree(
        &self,
        visited: &mut std::collections::HashSet<*const IntervalNode>,
    ) -> PyResult<()> {
        // Check for cycles (shouldn't happen but good to verify)
        let node_ptr = self as *const IntervalNode;
        if visited.contains(&node_ptr) {
            return Err(PyErr::new::<pyo3::exceptions::PyAssertionError, _>(
                "Error: Cycle detected in tree structure!",
            ));
        }
        visited.insert(node_ptr);

        // Verify interval is valid
        if self.interval.begin > self.interval.end {
            return Err(PyErr::new::<pyo3::exceptions::PyAssertionError, _>(
                format!(
                    "Error: Invalid interval in node: begin={} > end={}",
                    self.interval.begin, self.interval.end
                ),
            ));
        }

        // Verify max_end is at least this interval's end
        if self.max_end < self.interval.end {
            return Err(PyErr::new::<pyo3::exceptions::PyAssertionError, _>(
                format!(
                    "Error: max_end={} < interval.end={}",
                    self.max_end, self.interval.end
                ),
            ));
        }

        // Recursively verify children
        if let Some(ref left) = self.left {
            left.verify_subtree(visited)?;
        }

        if let Some(ref right) = self.right {
            right.verify_subtree(visited)?;
        }

        Ok(())
    }
}
