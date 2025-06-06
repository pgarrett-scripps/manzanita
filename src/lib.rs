use pyo3::exceptions::{PyTypeError, PyIndexError};

use pyo3::prelude::*;
use pyo3::types::{PyAny, PyFloat, PySlice, PyIterator, PyList, PyInt};
use std::cmp::Ordering;
use std::sync::Arc;

/// An interval representing a range from `begin` to `end`, with associated `data`.
#[pyclass]
#[derive(Clone)]
struct Interval {
    #[pyo3(get, set)]
    begin: f64,
    #[pyo3(get, set)]
    end: f64,
    #[pyo3(get)] // <- Add this to expose `data`
    data: PyObject,
}

#[pymethods]
impl Interval {
    /// Create a new Interval.
    #[new]
    fn new(begin: f64, end: f64, data: PyObject) -> Self {
        Interval { begin, end, data }
    }

    /// Checks if the interval overlaps a point.
    fn overlaps(&self, point: f64) -> bool {
        self.begin <= point && point < self.end
    }

    /// Checks if the interval overlaps a range.
    fn overlaps_range(&self, start: f64, end: f64) -> bool {
        self.begin < end && self.end > start
    }

    /// String representation of the interval.
    fn __repr__(&self, py: Python) -> PyResult<String> {
        let data_str = self.data.as_ref(py).str()?.to_str()?;
        Ok(format!("Interval({}, {}, {})", self.begin, self.end, data_str))
    }

    /// Implement len(interval)
    fn __len__(&self) -> usize {
        3
    }

    /// Implement interval[index]
    fn __getitem__(&self, idx: isize) -> PyResult<PyObject> {
        Python::with_gil(|py| match idx {
            0 => Ok(self.begin.into_py(py)),
            1 => Ok(self.end.into_py(py)),
            2 => Ok(self.data.clone()),
            _ => Err(PyIndexError::new_err("Index out of range")),
        })
    }

    /// Allow unpacking Interval objects as (begin, end, data) with custom iteration.
    fn __iter__(slf: PyRef<Self>) -> PyResult<Py<IntervalIter>> {
        let py = slf.py();
        let data = vec![
            slf.begin.into_py(py),
            slf.end.into_py(py),
            slf.data.clone(),
        ];
        Py::new(py, IntervalIter { data, index: 0 })
    }
}

/// Iterator for the Interval class.
#[pyclass]
struct IntervalIter {
    data: Vec<PyObject>,
    index: usize,
}

#[pymethods]
impl IntervalIter {
    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(&mut self) -> Option<PyObject> {
        if self.index < self.data.len() {
            let result = self.data[self.index].clone();
            self.index += 1;
            Some(result)
        } else {
            None
        }
    }
}

/// Node structure for an Interval Tree node
struct IntervalNode {
    interval: Arc<Interval>,
    max_end: f64,
    left: Option<Box<IntervalNode>>,
    right: Option<Box<IntervalNode>>,
}

impl IntervalNode {
    /// Constructor for creating a new IntervalNode
    fn new(interval: Arc<Interval>) -> Self {
        let max_end = interval.end;
        IntervalNode {
            interval,
            max_end,
            left: None,
            right: None,
        }
    }

    /// Updates the max_end value of the current node using total_cmp
    fn update_max_end(&mut self) {
        self.max_end = self.interval.end;
        if let Some(ref left) = self.left {
            if left.max_end.total_cmp(&self.max_end) == Ordering::Greater {
                self.max_end = left.max_end;
            }
        }
        if let Some(ref right) = self.right {
            if right.max_end.total_cmp(&self.max_end) == Ordering::Greater {
                self.max_end = right.max_end;
            }
        }
    }

    /// Inserts a new interval into the tree
    fn insert(&mut self, interval: Arc<Interval>) {
        if interval.begin < self.interval.begin {
            if let Some(ref mut left) = self.left {
                left.insert(interval);
            } else {
                self.left = Some(Box::new(IntervalNode::new(interval)));
            }
        } else {
            if let Some(ref mut right) = self.right {
                right.insert(interval);
            } else {
                self.right = Some(Box::new(IntervalNode::new(interval)));
            }
        }
        self.update_max_end();
    }

    /// Searches for all intervals overlapping with a given point
    fn search_point(&self, point: f64, result: &mut Vec<Arc<Interval>>) {
        if self.interval.overlaps(point) {
            result.push(self.interval.clone());
        }
        if let Some(ref left) = self.left {
            if left.max_end >= point {
                left.search_point(point, result);
            }
        }
        if let Some(ref right) = self.right {
            if point >= self.interval.begin {
                right.search_point(point, result);
            }
        }
    }

    fn search_range(&self, start: f64, end: f64, result: &mut Vec<Arc<Interval>>) {
        // Check if the current interval overlaps with the [start, end) range
        if self.interval.overlaps_range(start, end) {
            result.push(self.interval.clone());
        }

        // Search in the left subtree if its max_end is greater than the start
        if let Some(ref left) = self.left {
            if left.max_end > start { // Changed from `>=` to `>` to handle partial overlaps correctly
                left.search_range(start, end, result);
            }
        }

        // Search in the right subtree if the start of the interval is less than the end of the query range
        if let Some(ref right) = self.right {
            if self.interval.begin < end {  // Ensure right side intervals are considered
                right.search_range(start, end, result);
            }
        }
    }

    /// In-order traversal to collect all intervals in the tree.
    fn collect_intervals(&self, result: &mut Vec<Arc<Interval>>) {
        if let Some(ref left) = self.left {
            left.collect_intervals(result);
        }
        result.push(self.interval.clone());
        if let Some(ref right) = self.right {
            right.collect_intervals(result);
        }
    }

    /// Recursively count the number of intervals in the tree
    fn count_intervals(&self) -> usize {
        let left_count = if let Some(ref left) = self.left {
            left.count_intervals()
        } else {
            0
        };

        let right_count = if let Some(ref right) = self.right {
            right.count_intervals()
        } else {
            0
        };

        1 + left_count + right_count
    }
}

/// A basic interval tree supporting adding intervals and querying by point and range.
#[pyclass]
struct IntervalTree {
    root: Option<Box<IntervalNode>>,
}

#[pymethods]
impl IntervalTree {
    #[new]
    fn new() -> Self {
        IntervalTree { root: None }
    }

    /// Add an interval to the tree
    fn add(&mut self, interval: Interval) {
        let arc_interval = Arc::new(interval);
        if let Some(ref mut root) = self.root {
            root.as_mut().insert(arc_interval);
        } else {
            self.root = Some(Box::new(IntervalNode::new(arc_interval)));
        }
    }


    /// Query intervals overlapping a point
    fn at(&self, point: f64) -> Vec<Interval> {
        let mut result = Vec::new();
        if let Some(ref root) = self.root {
            let mut arc_result = Vec::new();
            root.search_point(point, &mut arc_result);
            for arc_interval in arc_result {
                result.push((*arc_interval).clone());
            }
        }
        result
    }

    /// Query intervals overlapping a range
    fn overlap(&self, start: f64, end: f64) -> Vec<Interval> {
        let mut result = Vec::new();
        if let Some(ref root) = self.root {
            let mut arc_result = Vec::new();
            root.search_range(start, end, &mut arc_result);
            for arc_interval in arc_result {
                result.push((*arc_interval).clone());
            }
        }
        result
    }

    /// Implement `__getitem__` to support tree[point] and tree[begin:end] access.
    fn __getitem__(&self, idx: &PyAny) -> PyResult<Vec<Interval>> {
        let py = idx.py();
        if idx.is_instance(py.get_type::<PyFloat>())? {
            let point: f64 = idx.extract()?;
            Ok(self.at(point))
        } else if idx.is_instance(py.get_type::<PySlice>())? {
            let slice = idx.downcast::<PySlice>()?;
            let start = match slice.getattr("start")?.extract::<Option<f64>>()? {
                Some(s) => s,
                None => f64::NEG_INFINITY,
            };
            let stop = match slice.getattr("stop")?.extract::<Option<f64>>()? {
                Some(s) => s,
                None => f64::INFINITY,
            };
            Ok(self.overlap(start, stop))
        } else {
            Err(PyErr::new::<PyTypeError, _>("Index must be a float or a slice"))
        }
    }

    /// Implement `__len__` to return the number of intervals in the tree
    fn __len__(&self) -> usize {
        if let Some(ref root) = self.root {
            root.count_intervals()
        } else {
            0
        }
    }

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

    fn __setitem__(&mut self, idx: &PyAny, value: &PyAny) -> PyResult<()> {
        let py = idx.py();
        let data = value.to_object(py); // Convert value to PyObject

        if idx.is_instance(py.get_type::<PySlice>())? {
            let slice = idx.downcast::<PySlice>()?;

            // Extract start and stop from the slice
            let start = match slice.getattr("start")?.extract::<Option<f64>>()? {
                Some(s) => s,
                None => return Err(PyErr::new::<PyTypeError, _>("Slice start cannot be None")),
            };
            let stop = match slice.getattr("stop")?.extract::<Option<f64>>()? {
                Some(s) => s,
                None => return Err(PyErr::new::<PyTypeError, _>("Slice stop cannot be None")),
            };

            // Create a new interval with the extracted start, stop, and data
            let interval = Interval::new(start, stop, data);
            self.add(interval);
            Ok(())
        } else if idx.is_instance(py.get_type::<PyFloat>())? || idx.is_instance(py.get_type::<PyInt>())? {
            // If the index is a float or int, treat it as a point
            let point: f64 = idx.extract()?;
            let epsilon = std::f64::EPSILON;
            // Create a new interval representing the point
            let interval = Interval::new(point, point + epsilon, data);
            self.add(interval);
            Ok(())
        } else {
            Err(PyErr::new::<PyTypeError, _>("Index must be a float, int, or a slice"))
        }
    }

    /// String representation of the IntervalTree.
    fn __repr__(&self) -> PyResult<String> {
        Ok(format!("IntervalTree()"))
    }

}

/// Python iterator for the IntervalTree.
#[pyclass]
struct IntervalTreeIter {
    intervals: Vec<Arc<Interval>>,
    index: usize,
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


/// Module initialization
#[pymodule]
fn manzanita(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Interval>()?;
    m.add_class::<IntervalIter>()?;
    m.add_class::<IntervalTree>()?;
    m.add_class::<IntervalTreeIter>()
}
