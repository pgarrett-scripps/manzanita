//! Interval tree data structure implementation.
//!
//! This module provides the main `IntervalTree` struct and its iterator, implementing
//! a high-performance interval tree with efficient insertion and query operations.

use crate::interval::Interval;
use crate::node::IntervalNode;
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
    pub fn new(intervals: Option<&PyAny>, start_inclusive: Option<bool>, end_inclusive: Option<bool>) -> PyResult<Self> {
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
    pub fn from_tuples(_cls: &PyType, tuples: &PyAny, start_inclusive: Option<bool>, end_inclusive: Option<bool>) -> PyResult<Self> {
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
                let data = Python::with_gil(|py| py.None());
                let interval = Interval::new(begin, end, data, Some(start_inclusive), Some(end_inclusive))?;
                tree.add(interval);
            } else if len == 3 {
                let begin: f64 = tuple.get_item(0)?.extract()?;
                let end: f64 = tuple.get_item(1)?.extract()?;
                let data = tuple.get_item(2)?.to_object(tuple.py());
                let interval = Interval::new(begin, end, data, Some(start_inclusive), Some(end_inclusive))?;
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
    /// * `begin` - The start of the interval (inclusive)
    /// * `end` - The end of the interval (exclusive)
    /// * `data` - Associated data for this interval
    /// 
    /// # Performance
    /// Average time complexity: O(log n)
    /// Worst case time complexity: O(n) for a degenerate tree
    pub fn addi(&mut self, begin: f64, end: f64, data: PyObject) -> PyResult<()> {
        let interval = Interval::new(begin, end, data, Some(self.start_inclusive), Some(self.end_inclusive))?;
        self.add(interval);
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
    /// * `start` - The start of the query range (inclusive)
    /// * `end` - The end of the query range (exclusive)
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
    /// * `data` - The data associated with the interval
    /// 
    /// # Returns
    /// `True` if the interval is in the tree, `False` otherwise
    pub fn containsi(&self, begin: f64, end: f64, data: PyObject) -> PyResult<bool> {
        let interval = Interval::new(begin, end, data, Some(self.start_inclusive), Some(self.end_inclusive))?;
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

    /// Returns the end coordinate of the rightmost interval.
    /// 
    /// # Returns  
    /// The maximum end value in the tree, or `None` if the tree is empty
    pub fn end(&self) -> Option<f64> {
        self.root.as_ref().map(|root| root.find_rightmost().end)
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
            let start = slice.getattr("start")?.extract::<Option<f64>>()?
                .unwrap_or(f64::NEG_INFINITY);
            let stop = slice.getattr("stop")?.extract::<Option<f64>>()?
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
            let start = slice.getattr("start")?.extract::<Option<f64>>()?
                .ok_or_else(|| PyTypeError::new_err("Slice start cannot be None"))?;
            let stop = slice.getattr("stop")?.extract::<Option<f64>>()?
                .ok_or_else(|| PyTypeError::new_err("Slice stop cannot be None"))?;
            
            let interval = Interval::new(start, stop, data, Some(self.start_inclusive), Some(self.end_inclusive))?;
            self.add(interval);
            Ok(())
        } else if let Ok(point) = idx.extract::<f64>() {
            // Create a point interval with minimal width
            let epsilon = f64::EPSILON.max(point.abs() * f64::EPSILON);
            let interval = Interval::new(point, point + epsilon, data, Some(self.start_inclusive), Some(self.end_inclusive))?;
            self.add(interval);
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
    /// * `data` - The data associated with the interval
    /// 
    /// # Errors
    /// Raises `ValueError` if the interval is not present in the tree
    pub fn removei(&mut self, begin: f64, end: f64, data: PyObject) -> PyResult<()> {
        let interval = Interval::new(begin, end, data, Some(self.start_inclusive), Some(self.end_inclusive))?;
        self.remove(interval)
    }

    /// Quietly removes an interval specified by individual parameters.
    /// 
    /// # Arguments
    /// * `begin` - The start of the interval
    /// * `end` - The end of the interval
    /// * `data` - The data associated with the interval
    /// 
    /// Does nothing if the interval is not present (no error raised)
    pub fn discardi(&mut self, begin: f64, end: f64, data: PyObject) -> PyResult<()> {
        let interval = Interval::new(begin, end, data, Some(self.start_inclusive), Some(self.end_inclusive))?;
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

    /// Supports deletion with `del tree[point]` and `del tree[start:end]` syntax.
    /// 
    /// # Arguments
    /// * `idx` - Either a float (for point deletion) or a slice (for range deletion)
    fn __delitem__(&mut self, idx: &PyAny) -> PyResult<()> {
        if let Ok(point) = idx.extract::<f64>() {
            self.remove_overlap(point, None);
            Ok(())
        } else if let Ok(slice) = idx.downcast::<PySlice>() {
            let start = slice.getattr("start")?.extract::<Option<f64>>()?
                .ok_or_else(|| PyTypeError::new_err("Slice start cannot be None"))?;
            let stop = slice.getattr("stop")?.extract::<Option<f64>>()?
                .ok_or_else(|| PyTypeError::new_err("Slice stop cannot be None"))?;
            
            self.remove_overlap(start, Some(stop));
            Ok(())
        } else {
            Err(PyTypeError::new_err("Index must be a number or slice"))
        }
    }

    /// String representation of the IntervalTree.
    fn __repr__(&self) -> String {
        format!("IntervalTree()")
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
