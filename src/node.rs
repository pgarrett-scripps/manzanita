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

    /// Updates the max_end value based on the current node and its children.
    /// This optimization allows for efficient search pruning.
    pub fn update_max_end(&mut self) {
        self.max_end = self.interval.end;
        
        if let Some(ref left) = self.left {
            self.max_end = self.max_end.max(left.max_end);
        }
        
        if let Some(ref right) = self.right {
            self.max_end = self.max_end.max(right.max_end);
        }
    }

    /// Inserts a new interval into the tree using BST ordering on begin values.
    pub fn insert(&mut self, interval: Arc<Interval>) {
        if interval.begin < self.interval.begin {
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

    /// Searches for all intervals overlapping with a given point.
    /// Uses max_end values for efficient pruning.
    pub fn search_point(&self, point: f64, result: &mut Vec<Arc<Interval>>) {
        if self.interval.overlaps(point) {
            result.push(self.interval.clone());
        }
        
        // Search left subtree if it might contain overlapping intervals
        if let Some(ref left) = self.left {
            if left.max_end > point {
                left.search_point(point, result);
            }
        }
        
        // Search right subtree if the point is not before this interval's start
        if let Some(ref right) = self.right {
            if point >= self.interval.begin {
                right.search_point(point, result);
            }
        }
    }

    /// Searches for all intervals overlapping with a given range [start, end).
    pub fn search_range(&self, start: f64, end: f64, result: &mut Vec<Arc<Interval>>) {
        if self.interval.overlaps_range(start, end) {
            result.push(self.interval.clone());
        }

        // Search left subtree if it might contain overlapping intervals
        if let Some(ref left) = self.left {
            if left.max_end > start {
                left.search_range(start, end, result);
            }
        }

        // Search right subtree if the query range extends past this interval's start
        if let Some(ref right) = self.right {
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

    /// Helper to check if two intervals have equal data (Python object comparison is complex)
    pub fn interval_data_equals(&self, a: &Arc<Interval>, b: &Arc<Interval>) -> bool {
        Python::with_gil(|py| {
            match (a.data.as_ref(py).is(b.data.as_ref(py)), 
                   a.data.as_ref(py).eq(&b.data.as_ref(py))) {
                (true, _) => true,  // Same object
                (false, Ok(true)) => true,  // Equal content
                _ => false,  // Different or comparison failed
            }
        })
    }

    /// Find the minimum (leftmost) interval in this subtree
    fn find_min(&self) -> Arc<Interval> {
        if let Some(ref left) = self.left {
            left.find_min()
        } else {
            self.interval.clone()
        }
    }

    /// Search for intervals that are enveloped by a range [start, end)
    pub fn search_enveloped(&self, start: f64, end: f64, result: &mut Vec<Arc<Interval>>) {
        // An interval is enveloped if it's completely contained within [start, end)
        if self.interval.begin >= start && self.interval.end <= end {
            result.push(self.interval.clone());
        }

        // Search left subtree if it might contain enveloped intervals
        if let Some(ref left) = self.left {
            if left.max_end > start {
                left.search_enveloped(start, end, result);
            }
        }

        // Search right subtree if it might contain enveloped intervals  
        if let Some(ref right) = self.right {
            if self.interval.begin < end {
                right.search_enveloped(start, end, result);
            }
        }
    }

    /// Check if a specific interval exists in the tree
    pub fn contains(&self, target: &Interval) -> bool {
        if self.interval.begin == target.begin && 
           self.interval.end == target.end &&
           self.interval_data_equals(&self.interval, &Arc::new(target.clone())) {
            true
        } else if target.begin < self.interval.begin {
            self.left.as_ref().map_or(false, |left| left.contains(target))
        } else {
            self.right.as_ref().map_or(false, |right| right.contains(target))
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
        
        if boxed_self.interval.begin == target.begin && 
           boxed_self.interval.end == target.end &&
           boxed_self.interval_data_equals(&boxed_self.interval, &Arc::new(target.clone())) {
            // This is the node to remove
            match (boxed_self.left.take(), boxed_self.right.take()) {
                (None, None) => None, // Leaf node, remove it
                (Some(left), None) => Some(left), // Only left child
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
                result = node.remove(&*interval);
            }
        }
        result
    }

    /// Remove all intervals that overlap with a range
    pub fn remove_overlap_range(self: Box<Self>, start: f64, end: f64) -> Option<Box<IntervalNode>> {
        let mut to_remove = Vec::new();
        self.collect_overlapping_range(start, end, &mut to_remove);
        
        let mut result = Some(self);
        for interval in to_remove {
            if let Some(node) = result {
                result = node.remove(&*interval);
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
                result = node.remove(&*interval);
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
            if left.max_end > point {
                left.collect_overlapping_point(point, result);
            }
        }
        
        if let Some(ref right) = self.right {
            if point >= self.interval.begin {
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
            if left.max_end > start {
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
}
