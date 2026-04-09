//! Interval tree data structure implementation.
//!
//! This module provides the main `IntervalTree` struct and its iterator, implementing
//! a high-performance interval tree with efficient insertion and query operations.

use crate::interval::Interval;
use crate::node::IntervalNode;
use ordered_float::OrderedFloat;
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyAny, PySlice, PyType};
use std::sync::Arc;

/// A high-performance interval tree supporting efficient insertion and query operations.
///
/// This data structure allows for fast querying of all intervals that overlap with
/// a given point or range. It uses a binary search tree ordered by interval start points,
/// with each node maintaining the maximum end value of its subtree for query optimization.
///
/// # Examples
/// ```python
/// from manzanita import Interval, IntervalTree
///
/// # Create a new tree
/// tree = IntervalTree()
///
/// # Add some intervals
/// tree.add(Interval(1.0, 3.0, "A"))
/// tree.add(Interval(2.0, 4.0, "B"))
/// tree.add(Interval(5.0, 7.0, "C"))
///
/// # Query for overlapping intervals
/// overlapping = tree.at(2.5)  # Returns intervals A and B
/// range_overlapping = tree.overlap(1.5, 5.5)  # Returns intervals A, B, and C
/// ```
#[pyclass]
#[derive(Clone)]
pub struct IntervalTree {
    pub(crate) root: Option<Box<IntervalNode>>,
    /// Default start boundary inclusivity for intervals created by this tree
    #[pyo3(get)]
    pub start_inclusive: bool,
    /// Default end boundary inclusivity for intervals created by this tree  
    #[pyo3(get)]
    pub end_inclusive: bool,
}

#[pymethods]
impl IntervalTree {
    /// Creates a new empty IntervalTree.
    ///
    /// # Arguments
    /// * `intervals` - Optional iterable of intervals to initialize the tree with
    /// * `start_inclusive` - Whether intervals should have inclusive start boundaries by default (default: true)
    /// * `end_inclusive` - Whether intervals should have inclusive end boundaries by default (default: false)
    #[new]
    #[pyo3(signature = (intervals=None, start_inclusive=true, end_inclusive=false))]
    pub fn new(
        intervals: Option<&PyAny>,
        start_inclusive: Option<bool>,
        end_inclusive: Option<bool>,
    ) -> PyResult<Self> {
        let start_inclusive = start_inclusive.unwrap_or(true);
        let end_inclusive = end_inclusive.unwrap_or(false);

        let mut tree = IntervalTree {
            root: None,
            start_inclusive,
            end_inclusive,
        };

        if let Some(intervals) = intervals {
            // Handle iterable of intervals
            let iter = intervals.iter()?;
            for item in iter {
                let interval: Interval = item?.extract()?;
                tree.add(interval);
            }
        }

        Ok(tree)
    }

    /// Creates an IntervalTree from an iterable of tuples.
    ///
    /// # Arguments
    /// * `tuples` - An iterable of (begin, end) or (begin, end, data) tuples
    /// * `start_inclusive` - Whether intervals should have inclusive start boundaries (default: true)
    /// * `end_inclusive` - Whether intervals should have inclusive end boundaries (default: false)
    ///
    /// # Returns
    /// A new IntervalTree containing the intervals
    #[classmethod]
    #[pyo3(signature = (tuples, start_inclusive=true, end_inclusive=false))]
    pub fn from_tuples(
        _cls: &PyType,
        tuples: &PyAny,
        start_inclusive: Option<bool>,
        end_inclusive: Option<bool>,
    ) -> PyResult<Self> {
        let start_inclusive = start_inclusive.unwrap_or(true);
        let end_inclusive = end_inclusive.unwrap_or(false);

        let mut tree = IntervalTree {
            root: None,
            start_inclusive,
            end_inclusive,
        };
        let iter = tuples.iter()?;

        for item in iter {
            let tuple = item?;
            let len = tuple.len()?;

            if len == 2 {
                let begin: f64 = tuple.get_item(0)?.extract()?;
                let end: f64 = tuple.get_item(1)?.extract()?;
                let interval =
                    Interval::new(begin, end, None, Some(start_inclusive), Some(end_inclusive))?;
                tree.add(interval);
            } else if len == 3 {
                let begin: f64 = tuple.get_item(0)?.extract()?;
                let end: f64 = tuple.get_item(1)?.extract()?;
                let data = tuple.get_item(2)?.to_object(tuple.py());
                let interval = Interval::new(
                    begin,
                    end,
                    Some(data),
                    Some(start_inclusive),
                    Some(end_inclusive),
                )?;
                tree.add(interval);
            } else {
                return Err(PyTypeError::new_err("Tuples must have 2 or 3 elements"));
            }
        }

        Ok(tree)
    }

    /// Adds an interval to the tree.
    ///
    /// # Arguments
    /// * `interval` - The interval to add to the tree
    ///
    /// # Performance
    /// Average time complexity: O(log n)
    /// Worst case time complexity: O(n) for a degenerate tree
    pub fn add(&mut self, interval: Interval) {
        let arc_interval = Arc::new(interval);
        match &mut self.root {
            Some(root) => root.insert(arc_interval),
            None => self.root = Some(Box::new(IntervalNode::new(arc_interval))),
        }
    }

    /// Adds an interval to the tree using individual parameters.
    ///
    /// # Arguments
    /// * `begin` - The start of the interval
    /// * `end` - The end of the interval
    /// * `data` - Associated data for this interval (default: None)
    ///
    /// # Performance
    /// Average time complexity: O(log n)
    /// Worst case time complexity: O(n) for a degenerate tree
    #[pyo3(signature = (begin, end, data=None))]
    pub fn addi(&mut self, begin: f64, end: f64, data: Option<PyObject>) -> PyResult<()> {
        let interval = Interval::new(
            begin,
            end,
            data,
            Some(self.start_inclusive),
            Some(self.end_inclusive),
        )?;
        self.add(interval);
        Ok(())
    }

    /// Adds an interval to the tree only if it's not already present.
    ///
    /// Unlike `add()`, this method checks for duplicates before inserting.
    pub fn append(&mut self, interval: Interval) {
        if !self.__contains__(interval.clone()) {
            self.add(interval);
        }
    }

    /// Adds an interval (by parameters) only if it's not already present.
    ///
    /// # Arguments
    /// * `begin` - The start of the interval
    /// * `end` - The end of the interval
    /// * `data` - Associated data for this interval (default: None)
    #[pyo3(signature = (begin, end, data=None))]
    pub fn appendi(&mut self, begin: f64, end: f64, data: Option<PyObject>) -> PyResult<()> {
        let interval = Interval::new(
            begin,
            end,
            data,
            Some(self.start_inclusive),
            Some(self.end_inclusive),
        )?;
        self.append(interval);
        Ok(())
    }

    /// Queries for all intervals that overlap with a given point.
    ///
    /// # Arguments
    /// * `point` - The point to query for overlapping intervals
    ///
    /// # Returns
    /// A vector of intervals that contain the given point
    ///
    /// # Performance
    /// Average time complexity: O(log n + k) where k is the number of overlapping intervals
    pub fn at(&self, point: f64) -> Vec<Interval> {
        let mut result = Vec::new();
        if let Some(ref root) = self.root {
            let mut arc_result = Vec::new();
            root.search_point(point, &mut arc_result);
            result.reserve(arc_result.len());
            for arc_interval in arc_result {
                result.push((*arc_interval).clone());
            }
        }
        result
    }

    /// Queries for all intervals that overlap with a given range [start, end).
    ///
    /// # Arguments
    /// * `start` - The start of the query range
    /// * `end` - The end of the query range
    ///
    /// # Returns
    /// A vector of intervals that overlap with the given range
    ///
    /// # Performance
    /// Average time complexity: O(log n + k) where k is the number of overlapping intervals
    pub fn overlap(&self, start: f64, end: f64) -> Vec<Interval> {
        let mut result = Vec::new();
        if let Some(ref root) = self.root {
            let mut arc_result = Vec::new();
            root.search_range(start, end, &mut arc_result);
            result.reserve(arc_result.len());
            for arc_interval in arc_result {
                result.push((*arc_interval).clone());
            }
        }
        result
    }

    /// Queries for all intervals that are enveloped by a given range [start, end).
    ///
    /// An interval is enveloped if it's completely contained within the search range.
    ///
    /// # Arguments
    /// * `start` - The start of the query range (inclusive)
    /// * `end` - The end of the query range (exclusive)
    ///
    /// # Returns
    /// A vector of intervals that are completely contained within the given range
    ///
    /// # Performance
    /// Average time complexity: O(log n + k) where k is the number of enveloped intervals
    pub fn envelop(&self, start: f64, end: f64) -> Vec<Interval> {
        let mut result = Vec::new();
        if let Some(ref root) = self.root {
            let mut arc_result = Vec::new();
            root.search_enveloped(start, end, &mut arc_result);
            result.reserve(arc_result.len());
            for arc_interval in arc_result {
                result.push((*arc_interval).clone());
            }
        }
        result
    }

    /// Checks if an interval is contained in the tree.
    ///
    /// # Arguments
    /// * `interval` - The interval to check for
    ///
    /// # Returns
    /// `True` if the interval is in the tree, `False` otherwise
    pub fn __contains__(&self, interval: Interval) -> bool {
        if let Some(ref root) = self.root {
            root.contains(&interval)
        } else {
            false
        }
    }

    /// Checks if an interval specified by individual parameters is in the tree.
    ///
    /// # Arguments
    /// * `begin` - The start of the interval
    /// * `end` - The end of the interval
    /// * `data` - The data associated with the interval (default: None)
    ///
    /// # Returns
    /// `True` if the interval is in the tree, `False` otherwise
    #[pyo3(signature = (begin, end, data=None))]
    pub fn containsi(&self, begin: f64, end: f64, data: Option<PyObject>) -> PyResult<bool> {
        let interval = Interval::new(
            begin,
            end,
            data,
            Some(self.start_inclusive),
            Some(self.end_inclusive),
        )?;
        Ok(self.__contains__(interval))
    }

    /// Checks if any intervals overlap with a point.
    ///
    /// # Arguments
    /// * `point_or_start` - Either a point (float) or start of range
    /// * `end` - Optional end of range for range overlap check
    ///
    /// # Returns
    /// `True` if any intervals overlap, `False` otherwise
    #[pyo3(signature = (point_or_start, end=None))]
    pub fn overlaps(&self, point_or_start: f64, end: Option<f64>) -> bool {
        if let Some(end_val) = end {
            !self.overlap(point_or_start, end_val).is_empty()
        } else {
            !self.at(point_or_start).is_empty()
        }
    }

    /// Returns all intervals in the tree.
    ///
    /// This is equivalent to iterating over the tree.
    ///
    /// # Returns
    /// A list of all intervals in the tree
    pub fn items(&self) -> Vec<Interval> {
        let mut result = Vec::new();
        if let Some(ref root) = self.root {
            let mut arc_result = Vec::new();
            root.collect_intervals(&mut arc_result);
            result.reserve(arc_result.len());
            for arc_interval in arc_result {
                result.push((*arc_interval).clone());
            }
        }
        result
    }

    /// Checks if the tree is empty.
    ///
    /// # Returns
    /// `True` if the tree contains no intervals, `False` otherwise
    pub fn is_empty(&self) -> bool {
        self.root.is_none()
    }

    /// Returns the begin coordinate of the leftmost interval.
    ///
    /// # Returns
    /// The minimum begin value in the tree, or `None` if the tree is empty
    pub fn begin(&self) -> Option<f64> {
        self.root.as_ref().map(|root| root.find_leftmost().begin)
    }

    /// Returns the maximum end coordinate across all intervals.
    ///
    /// # Returns
    /// The maximum end value in the tree, or `None` if the tree is empty
    pub fn end(&self) -> Option<f64> {
        self.root.as_ref().map(|root| root.max_end)
    }

    /// Support for `not tree` syntax.
    fn __bool__(&self) -> bool {
        !self.is_empty()
    }

    /// Supports indexing with `tree[point]` and `tree[start:end]` syntax.
    ///
    /// # Arguments
    /// * `idx` - Either a float (for point queries) or a slice (for range queries)
    ///
    /// # Returns
    /// A vector of overlapping intervals
    fn __getitem__(&self, idx: &PyAny) -> PyResult<Vec<Interval>> {
        if let Ok(point) = idx.extract::<f64>() {
            Ok(self.at(point))
        } else if let Ok(slice) = idx.downcast::<PySlice>() {
            let start = slice
                .getattr("start")?
                .extract::<Option<f64>>()?
                .unwrap_or(f64::NEG_INFINITY);
            let stop = slice
                .getattr("stop")?
                .extract::<Option<f64>>()?
                .unwrap_or(f64::INFINITY);
            Ok(self.overlap(start, stop))
        } else {
            Err(PyTypeError::new_err("Index must be a number or slice"))
        }
    }

    /// Returns the number of intervals in the tree.
    fn __len__(&self) -> usize {
        self.root.as_ref().map_or(0, |root| root.count_intervals())
    }

    /// Returns an iterator over all intervals in the tree.
    fn __iter__(slf: PyRef<Self>) -> PyResult<IntervalTreeIter> {
        let mut intervals = Vec::new();
        if let Some(ref root) = slf.root {
            root.collect_intervals(&mut intervals);
        }
        Ok(IntervalTreeIter {
            intervals,
            index: 0,
        })
    }

    /// Supports assignment with `tree[start:end] = data` and `tree[point] = data` syntax.
    /// Also supports deletion with `del tree[point]` and `del tree[start:end]` syntax.
    ///
    /// This creates and adds a new interval to the tree.
    fn __setitem__(&mut self, idx: &PyAny, value: &PyAny) -> PyResult<()> {
        let py = idx.py();
        let data = value.to_object(py);

        if let Ok(slice) = idx.downcast::<PySlice>() {
            let start = slice
                .getattr("start")?
                .extract::<Option<f64>>()?
                .ok_or_else(|| PyTypeError::new_err("Slice start cannot be None"))?;
            let stop = slice
                .getattr("stop")?
                .extract::<Option<f64>>()?
                .ok_or_else(|| PyTypeError::new_err("Slice stop cannot be None"))?;

            let interval = Interval::new(
                start,
                stop,
                Some(data),
                Some(self.start_inclusive),
                Some(self.end_inclusive),
            )?;
            self.add(interval);
            Ok(())
        } else if let Ok(point) = idx.extract::<f64>() {
            // Create a point interval with minimal width
            let epsilon = f64::EPSILON.max(point.abs() * f64::EPSILON);
            let interval = Interval::new(
                point,
                point + epsilon,
                Some(data),
                Some(self.start_inclusive),
                Some(self.end_inclusive),
            )?;
            self.add(interval);
            Ok(())
        } else {
            Err(PyTypeError::new_err("Index must be a number or slice"))
        }
    }

    /// Supports deletion with `del tree[point]` and `del tree[start:end]` syntax.
    ///
    /// For a point, removes all intervals overlapping that point.
    /// For a slice, removes all intervals overlapping that range.
    fn __delitem__(&mut self, idx: &PyAny) -> PyResult<()> {
        if let Ok(point) = idx.extract::<f64>() {
            self.remove_overlap(point, None);
            Ok(())
        } else if let Ok(slice) = idx.downcast::<PySlice>() {
            let start = slice
                .getattr("start")?
                .extract::<Option<f64>>()?
                .unwrap_or(f64::NEG_INFINITY);
            let stop = slice
                .getattr("stop")?
                .extract::<Option<f64>>()?
                .unwrap_or(f64::INFINITY);
            self.remove_overlap(start, Some(stop));
            Ok(())
        } else {
            Err(PyTypeError::new_err("Index must be a number or slice"))
        }
    }

    /// Removes an interval from the tree.
    ///
    /// # Arguments
    /// * `interval` - The interval to remove from the tree
    ///
    /// # Errors
    /// Raises `ValueError` if the interval is not present in the tree
    pub fn remove(&mut self, interval: Interval) -> PyResult<()> {
        if !self.__contains__(interval.clone()) {
            return Err(PyValueError::new_err("Interval not found in tree"));
        }

        if let Some(root) = self.root.take() {
            self.root = root.remove(&interval);
        }
        Ok(())
    }

    /// Quietly removes an interval from the tree.
    ///
    /// # Arguments
    /// * `interval` - The interval to remove from the tree
    ///
    /// Does nothing if the interval is not present (no error raised)
    pub fn discard(&mut self, interval: Interval) {
        if let Some(root) = self.root.take() {
            self.root = root.remove(&interval);
        }
    }

    /// Removes an interval specified by individual parameters.
    ///
    /// # Arguments
    /// * `begin` - The start of the interval
    /// * `end` - The end of the interval
    /// * `data` - The data associated with the interval (default: None)
    ///
    /// # Errors
    /// Raises `ValueError` if the interval is not present in the tree
    #[pyo3(signature = (begin, end, data=None))]
    pub fn removei(&mut self, begin: f64, end: f64, data: Option<PyObject>) -> PyResult<()> {
        let interval = Interval::new(
            begin,
            end,
            data,
            Some(self.start_inclusive),
            Some(self.end_inclusive),
        )?;
        self.remove(interval)
    }

    /// Quietly removes an interval specified by individual parameters.
    ///
    /// # Arguments
    /// * `begin` - The start of the interval
    /// * `end` - The end of the interval
    /// * `data` - The data associated with the interval (default: None)
    ///
    /// Does nothing if the interval is not present (no error raised)
    #[pyo3(signature = (begin, end, data=None))]
    pub fn discardi(&mut self, begin: f64, end: f64, data: Option<PyObject>) -> PyResult<()> {
        let interval = Interval::new(
            begin,
            end,
            data,
            Some(self.start_inclusive),
            Some(self.end_inclusive),
        )?;
        self.discard(interval);
        Ok(())
    }

    /// Removes all intervals that overlap with a point or range.
    ///
    /// # Arguments
    /// * `point_or_start` - Either a point (float) or start of range
    /// * `end` - Optional end of range for range overlap removal
    #[pyo3(signature = (point_or_start, end=None))]
    pub fn remove_overlap(&mut self, point_or_start: f64, end: Option<f64>) {
        if let Some(root) = self.root.take() {
            if let Some(end_val) = end {
                self.root = root.remove_overlap_range(point_or_start, end_val);
            } else {
                self.root = root.remove_overlap_point(point_or_start);
            }
        }
    }

    /// Removes all intervals that are enveloped by a range.
    ///
    /// # Arguments
    /// * `start` - The start of the range (inclusive)
    /// * `end` - The end of the range (exclusive)
    pub fn remove_envelop(&mut self, start: f64, end: f64) {
        if let Some(root) = self.root.take() {
            self.root = root.remove_enveloped(start, end);
        }
    }

    /// Removes all intervals from the tree.
    pub fn clear(&mut self) {
        self.root = None;
    }

    /// Removes and returns an arbitrary interval from the tree.
    ///
    /// This method removes and returns an arbitrary interval from the tree.
    /// The specific interval returned is implementation-dependent and should not be relied upon.
    ///
    /// # Returns
    /// The removed interval
    ///
    /// # Errors
    /// Raises `PyValueError` if the tree is empty
    ///
    /// # Examples
    /// ```python
    /// tree = IntervalTree([Interval(1, 3), Interval(2, 4)])
    /// interval = tree.pop()  # Returns and removes one of the intervals
    /// ```
    pub fn pop(&mut self) -> PyResult<Interval> {
        if let Some(root) = self.root.take() {
            // Get an arbitrary interval (we'll use the root interval)
            let popped_interval = (*root.interval).clone();

            // Remove that specific interval from the tree
            self.root = root.remove(&popped_interval);

            Ok(popped_interval)
        } else {
            Err(PyValueError::new_err("pop from empty IntervalTree"))
        }
    }

    /// String representation of the IntervalTree.
    fn __repr__(&self) -> String {
        "IntervalTree()".to_string()
    }

    // Set-like operations

    /// Returns a new tree containing the union of this tree and an iterable of intervals.
    ///
    /// # Arguments
    /// * `other` - An iterable of intervals to union with this tree
    ///
    /// # Returns
    /// A new IntervalTree containing all intervals from both sources
    pub fn union(&self, other: &PyAny) -> PyResult<IntervalTree> {
        let mut result = IntervalTree {
            root: None,
            start_inclusive: self.start_inclusive,
            end_inclusive: self.end_inclusive,
        };

        // Add all intervals from this tree
        for interval in self.items() {
            result.add(interval);
        }

        // Add intervals from the other iterable, skipping duplicates
        let iter = other.iter()?;
        for item in iter {
            let interval: Interval = item?.extract()?;
            if !result.__contains__(interval.clone()) {
                result.add(interval);
            }
        }

        Ok(result)
    }

    /// Updates this tree with intervals from an iterable.
    ///
    /// # Arguments
    /// * `other` - An iterable of intervals to add to this tree
    pub fn update(&mut self, other: &PyAny) -> PyResult<()> {
        let iter = other.iter()?;
        for item in iter {
            let interval: Interval = item?.extract()?;
            self.add(interval);
        }
        Ok(())
    }

    /// Returns a new tree containing intervals in this tree but not in the other iterable.
    ///
    /// # Arguments
    /// * `other` - An iterable of intervals to subtract from this tree
    ///
    /// # Returns
    /// A new IntervalTree containing intervals only in this tree
    pub fn difference(&self, other: &PyAny) -> PyResult<IntervalTree> {
        let mut result = IntervalTree {
            root: None,
            start_inclusive: self.start_inclusive,
            end_inclusive: self.end_inclusive,
        };

        // Collect intervals to subtract
        let mut to_subtract = Vec::new();
        let iter = other.iter()?;
        for item in iter {
            let interval: Interval = item?.extract()?;
            to_subtract.push(interval);
        }

        // Add intervals from this tree that are not in the other collection
        for interval in self.items() {
            if !to_subtract
                .iter()
                .any(|other_iv| intervals_equal(&interval, other_iv))
            {
                result.add(interval);
            }
        }

        Ok(result)
    }

    /// Removes intervals from this tree that are present in the other iterable.
    ///
    /// # Arguments
    /// * `other` - An iterable of intervals to remove from this tree
    pub fn difference_update(&mut self, other: &PyAny) -> PyResult<()> {
        let iter = other.iter()?;
        for item in iter {
            let interval: Interval = item?.extract()?;
            self.discard(interval);
        }
        Ok(())
    }

    /// Returns a new tree containing intervals present in both this tree and the other iterable.
    ///
    /// # Arguments
    /// * `other` - An iterable of intervals to intersect with this tree
    ///
    /// # Returns
    /// A new IntervalTree containing intervals present in both sources
    pub fn intersection(&self, other: &PyAny) -> PyResult<IntervalTree> {
        let mut result = IntervalTree {
            root: None,
            start_inclusive: self.start_inclusive,
            end_inclusive: self.end_inclusive,
        };

        // Collect intervals from other
        let mut other_intervals = Vec::new();
        let iter = other.iter()?;
        for item in iter {
            let interval: Interval = item?.extract()?;
            other_intervals.push(interval);
        }

        // Add intervals from this tree that are also in the other collection
        for interval in self.items() {
            if other_intervals
                .iter()
                .any(|other_iv| intervals_equal(&interval, other_iv))
            {
                result.add(interval);
            }
        }

        Ok(result)
    }

    /// Updates this tree to contain only intervals present in both this tree and the other iterable.
    ///
    /// # Arguments
    /// * `other` - An iterable of intervals to intersect with this tree
    pub fn intersection_update(&mut self, other: &PyAny) -> PyResult<()> {
        let intersection = self.intersection(other)?;
        self.root = intersection.root;
        Ok(())
    }

    /// Returns a new tree containing intervals in either tree but not in both.
    ///
    /// # Arguments
    /// * `other` - An iterable of intervals for symmetric difference
    ///
    /// # Returns
    /// A new IntervalTree containing intervals in either source but not both
    pub fn symmetric_difference(&self, other: &PyAny) -> PyResult<IntervalTree> {
        let mut result = IntervalTree {
            root: None,
            start_inclusive: self.start_inclusive,
            end_inclusive: self.end_inclusive,
        };

        // Collect intervals from both
        let self_items = self.items();
        let mut other_intervals = Vec::new();
        let iter = other.iter()?;
        for item in iter {
            let interval: Interval = item?.extract()?;
            other_intervals.push(interval);
        }

        // Add intervals from this tree that are not in other
        for interval in &self_items {
            if !other_intervals
                .iter()
                .any(|other_iv| intervals_equal(interval, other_iv))
            {
                result.add(interval.clone());
            }
        }

        // Add intervals from other that are not in this tree (consistent comparison)
        for interval in &other_intervals {
            if !self_items
                .iter()
                .any(|self_iv| intervals_equal(interval, self_iv))
            {
                result.add(interval.clone());
            }
        }

        Ok(result)
    }

    /// Updates this tree to contain intervals in either tree but not in both.
    ///
    /// # Arguments
    /// * `other` - An iterable of intervals for symmetric difference
    pub fn symmetric_difference_update(&mut self, other: &PyAny) -> PyResult<()> {
        let sym_diff = self.symmetric_difference(other)?;
        self.root = sym_diff.root;
        Ok(())
    }

    /// Checks if this tree is a subset of another iterable.
    ///
    /// # Arguments
    /// * `other` - An iterable of intervals to check against
    ///
    /// # Returns
    /// True if all intervals in this tree are also in the other iterable
    pub fn issubset(&self, other: &PyAny) -> PyResult<bool> {
        // Handle IntervalTree objects specially
        if let Ok(other_tree) = other.extract::<PyRef<IntervalTree>>() {
            // Check if all intervals in this tree are in other tree
            for interval in self.items() {
                if !other_tree.__contains__(interval) {
                    return Ok(false);
                }
            }
            return Ok(true);
        }

        // Handle other iterables
        let mut other_intervals = Vec::new();
        let iter = other.iter()?;
        for item in iter {
            let interval: Interval = item?.extract()?;
            other_intervals.push(interval);
        }

        // Check if all intervals in this tree are in other
        for interval in self.items() {
            if !other_intervals
                .iter()
                .any(|other_iv| intervals_equal(&interval, other_iv))
            {
                return Ok(false);
            }
        }

        Ok(true)
    }

    /// Checks if this tree is a superset of another iterable.
    ///
    /// # Arguments
    /// * `other` - An iterable of intervals to check against
    ///
    /// # Returns
    /// True if all intervals in the other iterable are also in this tree
    pub fn issuperset(&self, other: &PyAny) -> PyResult<bool> {
        // Handle IntervalTree objects specially
        if let Ok(other_tree) = other.extract::<PyRef<IntervalTree>>() {
            // Check if all intervals in other tree are in this tree
            for interval in other_tree.items() {
                if !self.__contains__(interval) {
                    return Ok(false);
                }
            }
            return Ok(true);
        }

        // Handle other iterables
        let iter = other.iter()?;
        for item in iter {
            let interval: Interval = item?.extract()?;
            if !self.__contains__(interval) {
                return Ok(false);
            }
        }
        Ok(true)
    }

    // Operator overloads for set operations

    /// Union operator: tree1 | tree2
    fn __or__(&self, other: &PyAny) -> PyResult<IntervalTree> {
        self.union(other)
    }

    /// In-place union operator: tree |= other
    fn __ior__(&mut self, other: &PyAny) -> PyResult<()> {
        self.update(other)
    }

    /// Difference operator: tree1 - tree2
    fn __sub__(&self, other: &PyAny) -> PyResult<IntervalTree> {
        self.difference(other)
    }

    /// In-place difference operator: tree -= other
    fn __isub__(&mut self, other: &PyAny) -> PyResult<()> {
        self.difference_update(other)
    }

    /// Intersection operator: tree1 & tree2
    fn __and__(&self, other: &PyAny) -> PyResult<IntervalTree> {
        self.intersection(other)
    }

    /// In-place intersection operator: tree &= other
    fn __iand__(&mut self, other: &PyAny) -> PyResult<()> {
        self.intersection_update(other)
    }

    /// Symmetric difference operator: tree1 ^ tree2
    fn __xor__(&self, other: &PyAny) -> PyResult<IntervalTree> {
        self.symmetric_difference(other)
    }

    /// In-place symmetric difference operator: tree ^= other
    fn __ixor__(&mut self, other: &PyAny) -> PyResult<()> {
        self.symmetric_difference_update(other)
    }

    /// Equality operator: tree1 == tree2
    fn __eq__(&self, other: &PyAny) -> PyResult<bool> {
        if let Ok(other_tree) = other.extract::<PyRef<IntervalTree>>() {
            let self_items = self.items();
            let other_items = other_tree.items();

            if self_items.len() != other_items.len() {
                return Ok(false);
            }

            // Check if all intervals in self are in other tree using __contains__
            for interval in &self_items {
                if !other_tree.__contains__(interval.clone()) {
                    return Ok(false);
                }
            }

            Ok(true)
        } else {
            Ok(false)
        }
    }

    /// Not equal operator: tree1 != tree2
    fn __ne__(&self, other: &PyAny) -> PyResult<bool> {
        Ok(!self.__eq__(other)?)
    }

    /// Less than or equal operator: tree1 <= tree2 (subset check)
    fn __le__(&self, other: &PyAny) -> PyResult<bool> {
        self.issubset(other)
    }

    /// Less than operator: tree1 < tree2 (proper subset check)
    fn __lt__(&self, other: &PyAny) -> PyResult<bool> {
        if self.issubset(other)? {
            // Check if it's a proper subset (self is subset but not equal)
            if let Ok(eq) = self.__eq__(other) {
                Ok(!eq)
            } else {
                Ok(true) // If we can't check equality, assume proper subset
            }
        } else {
            Ok(false)
        }
    }

    /// Greater than or equal operator: tree1 >= tree2 (superset check)
    fn __ge__(&self, other: &PyAny) -> PyResult<bool> {
        self.issuperset(other)
    }

    /// Greater than operator: tree1 > tree2 (proper superset check)
    fn __gt__(&self, other: &PyAny) -> PyResult<bool> {
        if self.issuperset(other)? {
            // Check if it's a proper superset (self is superset but not equal)
            if let Ok(eq) = self.__eq__(other) {
                Ok(!eq)
            } else {
                Ok(true) // If we can't check equality, assume proper superset
            }
        } else {
            Ok(false)
        }
    }

    /// Rich comparison method for Python
    fn __richcmp__(&self, other: &PyAny, op: pyo3::basic::CompareOp) -> PyResult<PyObject> {
        use pyo3::basic::CompareOp;

        let result = match op {
            CompareOp::Eq => self.__eq__(other)?,
            CompareOp::Ne => self.__ne__(other)?,
            CompareOp::Lt => self.__lt__(other)?,
            CompareOp::Le => self.__le__(other)?,
            CompareOp::Gt => self.__gt__(other)?,
            CompareOp::Ge => self.__ge__(other)?,
        };

        Ok(result.into_py(other.py()))
    }

    // Restructuring operations

    /// Chop out a range from the tree, removing all intervals that overlap the range
    /// and splitting intervals that extend beyond the range boundaries.
    ///
    /// # Arguments
    /// * `begin` - The start of the range to chop out
    /// * `end` - The end of the range to chop out
    /// * `datafunc` - Optional function to modify data of split intervals
    ///
    /// The datafunc takes two arguments: (interval, islower) where:
    /// - interval is the original interval being split
    /// - islower is True for the left side of the split, False for the right side
    ///
    /// # Examples
    /// ```python
    /// tree = IntervalTree([Interval(0, 10, "data")])
    /// tree.chop(3, 7)  # Results in [Interval(0, 3, "data"), Interval(7, 10, "data")]
    ///
    /// # With data function
    /// def datafunc(iv, islower):
    ///     return f"side: {'left' if islower else 'right'}"
    /// tree.chop(3, 7, datafunc)
    /// ```
    #[pyo3(signature = (begin, end, datafunc=None))]
    pub fn chop(&mut self, begin: f64, end: f64, datafunc: Option<PyObject>) -> PyResult<()> {
        if begin >= end {
            return Err(PyValueError::new_err("begin must be less than end"));
        }

        // Find all intervals that overlap with the chop range
        let overlapping = self.overlap(begin, end);

        // Remove all overlapping intervals first
        for interval in &overlapping {
            self.discard(interval.clone());
        }

        // Process each overlapping interval
        for interval in overlapping {
            // If interval extends before the chop range, add the left portion
            if interval.begin < begin {
                let new_data = if let Some(ref func) = datafunc {
                    Python::with_gil(|py| {
                        let args = (interval.clone(), true);
                        func.call1(py, args).unwrap_or(interval.data.clone())
                    })
                } else {
                    interval.data.clone()
                };

                let left_interval = Interval::new(
                    interval.begin,
                    begin,
                    Some(new_data),
                    Some(interval.start_inclusive),
                    Some(false), // End is always exclusive at the chop point
                )?;
                self.add(left_interval);
            }

            // If interval extends after the chop range, add the right portion
            if interval.end > end {
                let new_data = if let Some(ref func) = datafunc {
                    Python::with_gil(|py| {
                        let args = (interval.clone(), false);
                        func.call1(py, args).unwrap_or(interval.data.clone())
                    })
                } else {
                    interval.data.clone()
                };

                let right_interval = Interval::new(
                    end,
                    interval.end,
                    Some(new_data),
                    Some(true), // Start is always inclusive at the chop point
                    Some(interval.end_inclusive),
                )?;
                self.add(right_interval);
            }
        }

        Ok(())
    }

    /// Slice intervals at a specific point, splitting any intervals that contain the point.
    ///
    /// # Arguments
    /// * `point` - The point at which to slice intervals
    /// * `datafunc` - Optional function to modify data of split intervals
    ///
    /// The datafunc takes two arguments: (interval, islower) where:
    /// - interval is the original interval being split
    /// - islower is True for the left side of the split, False for the right side
    ///
    /// # Examples
    /// ```python
    /// tree = IntervalTree([Interval(0, 10, "data")])
    /// tree.slice(5)  # Results in [Interval(0, 5, "data"), Interval(5, 10, "data")]
    /// ```
    #[pyo3(signature = (point, datafunc=None))]
    pub fn slice(&mut self, point: f64, datafunc: Option<PyObject>) -> PyResult<()> {
        // Find all intervals that contain the slice point
        let containing = self.at(point);

        // Remove intervals that need to be split
        for interval in &containing {
            // Only split if the point is strictly inside the interval
            if interval.begin < point && point < interval.end {
                self.discard(interval.clone());
            }
        }

        // Split each interval that contains the point
        for interval in containing {
            if interval.begin < point && point < interval.end {
                // Create left side of split
                let left_data = if let Some(ref func) = datafunc {
                    Python::with_gil(|py| {
                        let args = (interval.clone(), true);
                        func.call1(py, args).unwrap_or(interval.data.clone())
                    })
                } else {
                    interval.data.clone()
                };

                let left_interval = Interval::new(
                    interval.begin,
                    point,
                    Some(left_data),
                    Some(interval.start_inclusive),
                    Some(false), // Split point is exclusive on left side
                )?;
                self.add(left_interval);

                // Create right side of split
                let right_data = if let Some(ref func) = datafunc {
                    Python::with_gil(|py| {
                        let args = (interval.clone(), false);
                        func.call1(py, args).unwrap_or(interval.data.clone())
                    })
                } else {
                    interval.data.clone()
                };

                let right_interval = Interval::new(
                    point,
                    interval.end,
                    Some(right_data),
                    Some(true), // Split point is inclusive on right side
                    Some(interval.end_inclusive),
                )?;
                self.add(right_interval);
            }
        }

        Ok(())
    }

    /// Creates a shallow copy of the tree.
    ///
    /// # Returns
    /// A new IntervalTree with shallow copies of all intervals
    pub fn copy(&self) -> IntervalTree {
        let mut new_tree = IntervalTree {
            root: None,
            start_inclusive: self.start_inclusive,
            end_inclusive: self.end_inclusive,
        };

        // Add all intervals to the new tree (this creates new Interval objects)
        for interval in self.items() {
            new_tree.add(interval);
        }

        new_tree
    }

    /// Splits all overlapping intervals at their boundary points.
    ///
    /// This method finds all points where intervals start or end, and slices
    /// at those points to ensure no intervals overlap.
    ///
    /// # Arguments
    /// * `datafunc` - Optional function to modify data of split intervals
    ///
    /// # Examples
    /// ```python
    /// tree = IntervalTree([Interval(1, 5, "A"), Interval(3, 7, "B")])
    /// tree.split_overlaps()  # Results in [1,3), [3,5), [5,7) with appropriate data
    /// ```
    #[pyo3(signature = (datafunc=None))]
    pub fn split_overlaps(&mut self, datafunc: Option<PyObject>) -> PyResult<()> {
        // Collect all boundary points
        let mut boundaries = std::collections::BTreeSet::new();
        for interval in self.items() {
            boundaries.insert(OrderedFloat(interval.begin));
            boundaries.insert(OrderedFloat(interval.end));
        }

        // Slice at each boundary point
        for boundary in boundaries {
            let point = boundary.into_inner();
            // Only slice if there are intervals that would be split
            let containing = self.at(point);
            if containing
                .iter()
                .any(|iv| iv.begin < point && point < iv.end)
            {
                self.slice(point, datafunc.clone())?;
            }
        }

        Ok(())
    }

    /// Merges overlapping intervals into single intervals.
    ///
    /// # Arguments
    /// * `datafunc` - Optional function to merge data of overlapping intervals
    /// * `strict` - If true, only merge intervals that strictly overlap (default: true)
    ///
    /// The datafunc takes a list of intervals to merge and returns the merged data.
    #[pyo3(signature = (datafunc=None, strict=true))]
    pub fn merge_overlaps(
        &mut self,
        datafunc: Option<PyObject>,
        strict: Option<bool>,
    ) -> PyResult<()> {
        let strict = strict.unwrap_or(true);
        let mut intervals = self.items();
        if intervals.is_empty() {
            return Ok(());
        }

        // Sort intervals by start point
        intervals.sort_by(|a, b| {
            a.begin
                .partial_cmp(&b.begin)
                .unwrap_or(std::cmp::Ordering::Equal)
        });

        self.clear();

        let mut merged = Vec::new();
        let mut current_group = vec![intervals[0].clone()];
        let mut group_max_end = intervals[0].end;

        for interval in intervals.into_iter().skip(1) {
            // Check if new interval overlaps with the group's accumulated envelope
            let overlaps_or_adjacent = if strict {
                // Strictly overlapping: new interval starts before the group ends
                interval.begin < group_max_end
            } else {
                // Also merge adjacent (touching) intervals
                interval.begin <= group_max_end
            };

            if overlaps_or_adjacent {
                current_group.push(interval.clone());
                if interval.end > group_max_end {
                    group_max_end = interval.end;
                }
            } else {
                // Merge current group and start new one
                let merged_interval = merge_interval_group(&current_group, datafunc.as_ref())?;
                merged.push(merged_interval);
                current_group = vec![interval.clone()];
                group_max_end = interval.end;
            }
        }

        // Don't forget the last group
        if !current_group.is_empty() {
            let merged_interval = merge_interval_group(&current_group, datafunc.as_ref())?;
            merged.push(merged_interval);
        }

        // Add all merged intervals back to tree
        for interval in merged {
            self.add(interval);
        }

        Ok(())
    }

    /// Merges intervals with identical ranges.
    ///
    /// # Arguments
    /// * `datafunc` - Optional function to merge data of equal intervals
    ///
    /// The datafunc takes a list of intervals to merge and returns the merged data.
    #[pyo3(signature = (datafunc=None))]
    pub fn merge_equals(&mut self, datafunc: Option<PyObject>) -> PyResult<()> {
        let intervals = self.items();
        if intervals.is_empty() {
            return Ok(());
        }

        // Group intervals by their range
        let mut groups: std::collections::HashMap<
            (OrderedFloat<f64>, OrderedFloat<f64>),
            Vec<Interval>,
        > = std::collections::HashMap::new();

        for interval in intervals {
            let key = (OrderedFloat(interval.begin), OrderedFloat(interval.end));
            groups.entry(key).or_default().push(interval);
        }

        // If no duplicates and no datafunc, nothing to do
        let has_duplicates = groups.values().any(|g| g.len() > 1);
        if !has_duplicates && datafunc.is_none() {
            return Ok(());
        }

        self.clear();

        // Merge each group
        for group in groups.values() {
            if group.len() == 1 && datafunc.is_none() {
                self.add(group[0].clone());
            } else if datafunc.is_some() {
                let merged_interval = merge_interval_group(group, datafunc.as_ref())?;
                self.add(merged_interval);
            } else {
                // No datafunc: merged interval has None data (matches intervaltree behavior)
                let iv = &group[0];
                let merged = Interval::new(
                    iv.begin,
                    iv.end,
                    None,
                    Some(iv.start_inclusive),
                    Some(iv.end_inclusive),
                )?;
                self.add(merged);
            }
        }

        Ok(())
    }

    /// Merges adjacent intervals.
    ///
    /// # Arguments
    /// * `datafunc` - Optional function to merge data of adjacent intervals
    /// * `max_dist` - Maximum distance between intervals to be considered adjacent (default: 0.0)
    /// * `merge_overlaps` - Whether to also merge overlapping intervals (default: false)
    ///
    /// The datafunc takes a list of intervals to merge and returns the merged data.
    #[pyo3(signature = (datafunc=None, max_dist=0.0, merge_overlaps=false))]
    pub fn merge_neighbors(
        &mut self,
        datafunc: Option<PyObject>,
        max_dist: Option<f64>,
        merge_overlaps: Option<bool>,
    ) -> PyResult<()> {
        let max_dist = max_dist.unwrap_or(0.0);
        let merge_overlaps = merge_overlaps.unwrap_or(false);

        let mut intervals = self.items();
        if intervals.is_empty() {
            return Ok(());
        }

        // Sort intervals by start point
        intervals.sort_by(|a, b| {
            a.begin
                .partial_cmp(&b.begin)
                .unwrap_or(std::cmp::Ordering::Equal)
        });

        self.clear();

        let mut merged = Vec::new();
        let mut current_group = vec![intervals[0].clone()];

        for interval in intervals.into_iter().skip(1) {
            let last_in_group = &current_group[current_group.len() - 1];

            // Calculate distance between intervals considering boundary inclusivity
            let distance = if last_in_group.end_inclusive && interval.start_inclusive {
                // If both boundaries are inclusive, touching intervals have distance 0
                (interval.begin - last_in_group.end).abs()
            } else {
                // Otherwise, use the actual distance
                interval.begin - last_in_group.end
            };

            let should_merge = distance <= max_dist
                || (merge_overlaps && last_in_group.overlaps_interval(&interval))
                || (!merge_overlaps && intervals_are_adjacent(last_in_group, &interval));

            if should_merge {
                current_group.push(interval);
            } else {
                // Merge current group and start new one
                let merged_interval = merge_interval_group(&current_group, datafunc.as_ref())?;
                merged.push(merged_interval);
                current_group = vec![interval];
            }
        }

        // Don't forget the last group
        if !current_group.is_empty() {
            let merged_interval = merge_interval_group(&current_group, datafunc.as_ref())?;
            merged.push(merged_interval);
        }

        // Add all merged intervals back to tree
        for interval in merged {
            self.add(interval);
        }

        Ok(())
    }

    /// Returns a number between 0 and 1, indicating how suboptimal the tree is.
    ///
    /// The lower the score, the better the tree structure. This number roughly represents
    /// the fraction of flawed intervals in the tree.
    ///
    /// # Arguments
    /// * `full_report` - If true, returns a detailed report as a dictionary (default: false)
    ///
    /// # Returns
    /// Either a float score (0.0 to 1.0) or a dictionary with detailed metrics
    ///
    /// # Examples
    /// ```python
    /// tree = IntervalTree([Interval(1, 3), Interval(2, 4)])
    /// score = tree.score()  # Returns float between 0.0 and 1.0
    /// report = tree.score(full_report=True)  # Returns detailed dict
    /// ```
    #[pyo3(signature = (full_report=false))]
    pub fn score(&self, full_report: Option<bool>) -> PyResult<PyObject> {
        let full_report = full_report.unwrap_or(false);

        let n = self.__len__();
        if n <= 2 {
            return Python::with_gil(|py| {
                if full_report {
                    let report = pyo3::types::PyDict::new(py);
                    report.set_item("depth", 0.0)?;
                    report.set_item("s_center", 0.0)?;
                    report.set_item("_cumulative", 0.0)?;
                    Ok(report.into())
                } else {
                    Ok(0.0f64.into_py(py))
                }
            });
        }

        let m = if let Some(ref root) = self.root {
            root.count_nodes()
        } else {
            0
        };

        // Calculate s_center score
        let s_center_score = {
            let raw = n.saturating_sub(m);
            let maximum = n.saturating_sub(1);
            if maximum == 0 {
                0.0
            } else {
                raw as f64 / maximum as f64
            }
        };

        // Calculate depth score
        let depth_score = if let Some(ref root) = self.root {
            root.depth_score(n, m)
        } else {
            0.0
        };

        let cumulative = depth_score.max(s_center_score);

        Python::with_gil(|py| {
            if full_report {
                let report = pyo3::types::PyDict::new(py);
                report.set_item("depth", depth_score)?;
                report.set_item("s_center", s_center_score)?;
                report.set_item("_cumulative", cumulative)?;
                Ok(report.into())
            } else {
                Ok(cumulative.into_py(py))
            }
        })
    }

    /// Returns a minimum-spanning Interval that encloses all intervals in the tree.
    ///
    /// # Returns
    /// An Interval spanning from the minimum begin to the maximum end, or None if empty
    pub fn range(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| match &self.root {
            None => Ok(py.None()),
            Some(root) => {
                let begin = root.find_leftmost().begin;
                let end = root.max_end;
                let interval = Interval::new(
                    begin,
                    end,
                    None,
                    Some(self.start_inclusive),
                    Some(self.end_inclusive),
                )?;
                Ok(Py::new(py, interval)?.to_object(py))
            }
        })
    }

    /// Returns the length of the minimum-spanning interval of all intervals in the tree.
    ///
    /// # Returns
    /// The span (max end - min begin), or 0 if the tree is empty
    pub fn span(&self) -> f64 {
        match &self.root {
            None => 0.0,
            Some(root) => {
                let begin = root.find_leftmost().begin;
                let end = root.max_end;
                end - begin
            }
        }
    }

    /// Returns True if this tree has no intervals in common with the other iterable.
    ///
    /// This is a set-based check: two trees are disjoint if they share no
    /// identical intervals (same begin, end, and data).
    pub fn isdisjoint(&self, other: &PyAny) -> PyResult<bool> {
        if let Ok(other_tree) = other.extract::<PyRef<IntervalTree>>() {
            for interval in self.items() {
                if other_tree.__contains__(interval) {
                    return Ok(false);
                }
            }
            return Ok(true);
        }

        let mut other_intervals = Vec::new();
        let iter = other.iter()?;
        for item in iter {
            let interval: Interval = item?.extract()?;
            other_intervals.push(interval);
        }

        for interval in self.items() {
            if other_intervals
                .iter()
                .any(|other_iv| intervals_equal(&interval, other_iv))
            {
                return Ok(false);
            }
        }

        Ok(true)
    }

    /// Returns a dict mapping each interval to a set of intervals contained within it.
    ///
    /// Only intervals that contain at least one other interval appear as keys.
    /// An interval A contains interval B if A.begin <= B.begin and A.end >= B.end.
    pub fn find_nested(&self) -> PyResult<PyObject> {
        Python::with_gil(|py| {
            let dict = pyo3::types::PyDict::new(py);
            let all_intervals = self.items();

            for (i, parent) in all_intervals.iter().enumerate() {
                let mut nested_py: Vec<PyObject> = Vec::new();
                for (j, child) in all_intervals.iter().enumerate() {
                    if i == j {
                        continue;
                    }
                    if parent.begin <= child.begin && parent.end >= child.end {
                        nested_py.push(Py::new(py, child.clone())?.to_object(py));
                    }
                }

                if !nested_py.is_empty() {
                    let parent_py = Py::new(py, parent.clone())?.to_object(py);
                    let set = pyo3::types::PySet::new(py, &nested_py)?;
                    dict.set_item(parent_py, set)?;
                }
            }

            Ok(dict.into())
        })
    }

    /// Pretty-prints the structure of the tree for debugging.
    ///
    /// # Arguments
    /// * `tostring` - If true, returns the string instead of printing it (default: false)
    #[pyo3(signature = (tostring=false))]
    pub fn print_structure(&self, tostring: Option<bool>) -> PyResult<PyObject> {
        let tostring = tostring.unwrap_or(false);
        let mut output = String::new();

        if let Some(ref root) = self.root {
            Self::format_node_recursive(root, &mut output, 0);
        } else {
            output.push_str("<empty IntervalTree>");
        }

        Python::with_gil(|py| {
            if tostring {
                Ok(output.into_py(py))
            } else {
                let builtins = py.import("builtins")?;
                builtins.call_method1("print", (&output,))?;
                Ok(py.None())
            }
        })
    }

    /// FOR DEBUGGING ONLY
    /// Checks the tree to ensure that all invariants are held.
    ///
    /// This method performs comprehensive validation of the tree structure,
    /// including consistency checks between the tree nodes and internal data.
    ///
    /// # Errors
    /// Raises AssertionError if any invariant is violated
    pub fn verify(&self) -> PyResult<()> {
        if let Some(ref root) = self.root {
            // Check that all intervals in tree are valid Interval objects
            let all_intervals = self.items();
            for interval in &all_intervals {
                // Check that it's a valid interval (begin <= end)
                if interval.begin > interval.end {
                    return Err(PyErr::new::<pyo3::exceptions::PyAssertionError, _>(
                        format!(
                            "Error: Invalid interval found: begin ({}) > end ({})",
                            interval.begin, interval.end
                        ),
                    ));
                }

                // Check for null intervals (begin == end)
                if interval.is_null() {
                    return Err(PyErr::new::<pyo3::exceptions::PyAssertionError, _>(
                        format!("Error: Null Interval objects not allowed in IntervalTree: Interval({}, {})", 
                               interval.begin, interval.end)
                    ));
                }
            }

            // Verify internal tree structure
            let mut visited = std::collections::HashSet::new();
            root.verify_subtree(&mut visited)?;

            // Verify that tree contains exactly the intervals we expect
            let tree_intervals = self.items();
            let tree_count = tree_intervals.len();
            let node_count = root.count_intervals();

            if tree_count != node_count {
                return Err(PyErr::new::<pyo3::exceptions::PyAssertionError, _>(
                    format!("Error: Tree interval count mismatch! Tree reports {} intervals but nodes contain {}",
                           tree_count, node_count)
                ));
            }

            // Verify BST property: left subtree intervals have begin <= root.begin,
            // right subtree intervals have begin >= root.begin
            Self::verify_bst_property_recursive(root, f64::NEG_INFINITY, f64::INFINITY)?;

            // Verify max_end properties are correct
            Self::verify_max_end_property_recursive(root)?;
        } else {
            // Verify empty tree
            if !self.is_empty() {
                return Err(PyErr::new::<pyo3::exceptions::PyAssertionError, _>(
                    "Error: Tree reports non-empty but root is None!",
                ));
            }
        }

        Ok(())
    }
}

impl IntervalTree {
    /// Helper to format a node and its children for print_structure
    fn format_node_recursive(node: &IntervalNode, output: &mut String, indent: usize) {
        Python::with_gil(|py| {
            let data_str = node
                .interval
                .data
                .as_ref(py)
                .str()
                .map(|s| s.to_string())
                .unwrap_or_else(|_| "?".to_string());
            let start_bracket = if node.interval.start_inclusive {
                "["
            } else {
                "("
            };
            let end_bracket = if node.interval.end_inclusive {
                "]"
            } else {
                ")"
            };
            let spaces = "  ".repeat(indent);
            output.push_str(&format!(
                "{}Node: Interval{}{}, {}{} data={}, max_end={}\n",
                spaces,
                start_bracket,
                node.interval.begin,
                node.interval.end,
                end_bracket,
                data_str,
                node.max_end
            ));
        });

        if let Some(ref left) = node.left {
            let spaces = "  ".repeat(indent + 1);
            output.push_str(&format!("{}L:\n", spaces));
            Self::format_node_recursive(left, output, indent + 2);
        }
        if let Some(ref right) = node.right {
            let spaces = "  ".repeat(indent + 1);
            output.push_str(&format!("{}R:\n", spaces));
            Self::format_node_recursive(right, output, indent + 2);
        }
    }

    /// Recursive helper to verify BST property for a node
    fn verify_bst_property_recursive(
        node: &IntervalNode,
        min_begin: f64,
        max_begin: f64,
    ) -> PyResult<()> {
        // Check that this node's interval.begin is within the allowed range
        if node.interval.begin < min_begin || node.interval.begin > max_begin {
            return Err(PyErr::new::<pyo3::exceptions::PyAssertionError, _>(
                format!(
                    "Error: BST property violated! Node interval.begin={} not in range [{}, {}]",
                    node.interval.begin, min_begin, max_begin
                ),
            ));
        }

        // Recursively check left subtree (should have begin <= this.begin)
        if let Some(ref left) = node.left {
            Self::verify_bst_property_recursive(left, min_begin, node.interval.begin)?;
        }

        // Recursively check right subtree (should have begin >= this.begin)
        if let Some(ref right) = node.right {
            Self::verify_bst_property_recursive(right, node.interval.begin, max_begin)?;
        }

        Ok(())
    }

    /// Recursive helper to verify max_end property for a node
    fn verify_max_end_property_recursive(node: &IntervalNode) -> PyResult<()> {
        // Calculate what max_end should be
        let mut expected_max_end = node.interval.end;

        if let Some(ref left) = node.left {
            Self::verify_max_end_property_recursive(left)?;
            if left.max_end > expected_max_end {
                expected_max_end = left.max_end;
            }
        }

        if let Some(ref right) = node.right {
            Self::verify_max_end_property_recursive(right)?;
            if right.max_end > expected_max_end {
                expected_max_end = right.max_end;
            }
        }

        // Check that stored max_end matches calculated value
        if (node.max_end - expected_max_end).abs() > f64::EPSILON {
            return Err(PyErr::new::<pyo3::exceptions::PyAssertionError, _>(
                format!(
                    "Error: max_end property violated! Node has max_end={} but should be {}",
                    node.max_end, expected_max_end
                ),
            ));
        }

        Ok(())
    }
}

/// Python iterator for the IntervalTree.
#[pyclass]
pub struct IntervalTreeIter {
    pub(crate) intervals: Vec<Arc<Interval>>,
    pub(crate) index: usize,
}

#[pymethods]
impl IntervalTreeIter {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<Self>, py: Python) -> Option<Py<Interval>> {
        if slf.index < slf.intervals.len() {
            let interval = slf.intervals[slf.index].clone();
            slf.index += 1;
            Some(Py::new(py, (*interval).clone()).unwrap())
        } else {
            None
        }
    }
}

/// Helper function to check if two intervals are equal
fn intervals_equal(a: &Interval, b: &Interval) -> bool {
    a.begin == b.begin
        && a.end == b.end
        && a.start_inclusive == b.start_inclusive
        && a.end_inclusive == b.end_inclusive
        && Python::with_gil(|py| {
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

/// Helper function to check if two intervals are adjacent (touching boundaries)
fn intervals_are_adjacent(a: &Interval, b: &Interval) -> bool {
    // Intervals are adjacent if one ends where the other begins, and at least one boundary is inclusive
    (a.end == b.begin && (a.end_inclusive || b.start_inclusive))
        || (b.end == a.begin && (b.end_inclusive || a.start_inclusive))
}

/// Helper function to merge a group of intervals
fn merge_interval_group(intervals: &[Interval], datafunc: Option<&PyObject>) -> PyResult<Interval> {
    if intervals.is_empty() {
        return Err(PyValueError::new_err("Cannot merge empty interval group"));
    }

    if intervals.len() == 1 {
        return Ok(intervals[0].clone());
    }

    // Find the span of all intervals
    let min_begin = intervals
        .iter()
        .map(|iv| iv.begin)
        .fold(f64::INFINITY, f64::min);
    let max_end = intervals
        .iter()
        .map(|iv| iv.end)
        .fold(f64::NEG_INFINITY, f64::max);

    // Determine boundary inclusivity for the merged interval
    // Start: inclusive if any of the intervals with min_begin are start_inclusive
    // End: inclusive if any of the intervals with max_end are end_inclusive
    let start_inclusive = intervals
        .iter()
        .filter(|iv| iv.begin == min_begin)
        .any(|iv| iv.start_inclusive);

    let end_inclusive = intervals
        .iter()
        .filter(|iv| iv.end == max_end)
        .any(|iv| iv.end_inclusive);

    // Merge data
    let merged_data = if let Some(func) = datafunc {
        Python::with_gil(|py| {
            // Convert intervals to Python objects for the function call
            let py_intervals: Vec<PyObject> = intervals
                .iter()
                .map(|iv| Py::new(py, iv.clone()).unwrap().to_object(py))
                .collect();
            let interval_list = pyo3::types::PyList::new(py, &py_intervals);
            func.call1(py, (interval_list,))
                .unwrap_or_else(|_| intervals[0].data.clone())
        })
    } else {
        // Default: use first interval's data
        intervals[0].data.clone()
    };

    Interval::new(
        min_begin,
        max_end,
        Some(merged_data),
        Some(start_inclusive),
        Some(end_inclusive),
    )
}
