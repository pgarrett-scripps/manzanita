//! Interval data structure and related functionality.
//!
//! This module provides the `Interval` struct which represents an interval [begin, end]
//! with configurable boundary inclusivity and associated data, and its Python iterator implementation.

use pyo3::exceptions::PyIndexError;
use pyo3::prelude::*;

/// Defines whether an interval boundary is inclusive or exclusive.
#[pyclass]
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum BoundaryType {
    /// Boundary is inclusive (includes the boundary point)
    Inclusive,
    /// Boundary is exclusive (excludes the boundary point)  
    Exclusive,
}

/// An interval representing a range from `begin` to `end`, with associated `data`.
///
/// This structure represents an interval with configurable boundary inclusivity.
/// By default, intervals are half-open [begin, end) with inclusive start and exclusive end.
///
/// # Examples
/// ```python
/// from manzanita import Interval
///
/// # Create a default half-open interval [1.0, 5.0) with string data
/// interval = Interval(1.0, 5.0, "my data")
///
/// # Check if a point overlaps
/// assert interval.overlaps(3.0) == True
/// assert interval.overlaps(5.0) == False  # end is exclusive by default
/// ```
#[pyclass]
#[derive(Clone)]
pub struct Interval {
    /// The start of the interval
    #[pyo3(get, set)]
    pub begin: f64,
    /// The end of the interval
    #[pyo3(get, set)]
    pub end: f64,
    /// Associated data for this interval
    #[pyo3(get)]
    pub data: PyObject,
    /// Whether the start boundary is inclusive or exclusive
    #[pyo3(get)]
    pub start_inclusive: bool,
    /// Whether the end boundary is inclusive or exclusive
    #[pyo3(get)]
    pub end_inclusive: bool,
}

#[pymethods]
impl Interval {
    /// Create a new Interval.
    ///
    /// # Arguments
    /// * `begin` - The start of the interval
    /// * `end` - The end of the interval
    /// * `data` - Associated data for this interval (default: None)
    /// * `start_inclusive` - Whether the start boundary is inclusive (default: true)
    /// * `end_inclusive` - Whether the end boundary is inclusive (default: false)
    ///
    /// # Errors
    /// Returns a `PyTypeError` if `begin > end`.
    #[new]
    #[pyo3(signature = (begin, end, data=None, start_inclusive=true, end_inclusive=false))]
    pub fn new(
        begin: f64,
        end: f64,
        data: Option<PyObject>,
        start_inclusive: Option<bool>,
        end_inclusive: Option<bool>,
    ) -> PyResult<Self> {
        if begin >= end {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(format!(
                "Invalid interval: begin ({}) must be < end ({})",
                begin, end
            )));
        }

        let data = data.unwrap_or_else(|| Python::with_gil(|py| py.None()));

        Ok(Interval {
            begin,
            end,
            data,
            start_inclusive: start_inclusive.unwrap_or(true),
            end_inclusive: end_inclusive.unwrap_or(false),
        })
    }

    /// Checks if the interval overlaps a point.
    ///
    /// Returns `true` if the point falls within the interval boundaries based on inclusivity settings.
    pub fn overlaps(&self, point: f64) -> bool {
        let start_check = if self.start_inclusive {
            self.begin <= point
        } else {
            self.begin < point
        };

        let end_check = if self.end_inclusive {
            point <= self.end
        } else {
            point < self.end
        };

        start_check && end_check
    }

    /// Checks if the interval overlaps a range.
    ///
    /// Returns `true` if this interval overlaps with the range [start, end) based on boundary inclusivity.
    /// The range parameter is assumed to be [start, end) (start inclusive, end exclusive).
    pub fn overlaps_range(&self, start: f64, end: f64) -> bool {
        // Two ranges overlap if they have any point in common
        // For interval [a,b] and range [start,end):
        // - No overlap if: b < start OR a >= end (considering boundary inclusivity)
        // - Overlap if: NOT (no overlap condition)

        let no_overlap = if self.end_inclusive {
            // If interval end is inclusive, no overlap if self.end < start
            self.end < start
        } else {
            // If interval end is exclusive, no overlap if self.end <= start
            self.end <= start
        } || if self.start_inclusive {
            // If interval start is inclusive, no overlap if self.begin >= end
            self.begin >= end
        } else {
            // If interval start is exclusive, no overlap if self.begin >= end (same condition)
            self.begin >= end
        };

        !no_overlap
    }

    /// Checks if this interval overlaps with another interval.
    ///
    /// Returns `true` if the intervals overlap based on their boundary inclusivity.
    pub fn overlaps_interval(&self, other: &Interval) -> bool {
        // Two intervals overlap if: self.begin < other.end AND other.begin < self.end
        // But we need to consider boundary inclusivity for touching intervals

        let self_starts_before_other_ends = if self.start_inclusive && other.end_inclusive {
            self.begin <= other.end // If both boundaries are inclusive, use <=
        } else {
            self.begin < other.end // Otherwise use <
        };

        let other_starts_before_self_ends = if other.start_inclusive && self.end_inclusive {
            other.begin <= self.end // If both boundaries are inclusive, use <=
        } else {
            other.begin < self.end // Otherwise use <
        };

        self_starts_before_other_ends && other_starts_before_self_ends
    }

    /// Checks if this interval is completely contained within another interval.
    ///
    /// Returns `true` if this interval is enveloped by the other interval.
    pub fn enveloped_by_interval(&self, other: &Interval) -> bool {
        let start_contained = if other.start_inclusive {
            other.begin <= self.begin
        } else {
            other.begin < self.begin
        };

        let end_contained = if other.end_inclusive {
            self.end <= other.end
        } else {
            self.end < other.end
        };

        start_contained && end_contained
    }

    /// Returns the length/span of the interval.
    pub fn length(&self) -> f64 {
        self.end - self.begin
    }

    /// Checks if this interval is null (zero length).
    pub fn is_null(&self) -> bool {
        self.begin == self.end
    }

    /// Checks if the interval contains a point (alias for overlaps).
    ///
    /// Provided for compatibility with the `intervaltree` library.
    pub fn contains_point(&self, point: f64) -> bool {
        self.overlaps(point)
    }

    /// Checks if this interval completely contains another interval.
    ///
    /// Returns `true` if the other interval's range is within this interval's range.
    pub fn contains_interval(&self, other: &Interval) -> bool {
        self.begin <= other.begin && self.end >= other.end
    }

    /// Returns the size of the gap between this interval and the given point or interval.
    ///
    /// Returns 0 if they overlap.
    pub fn distance_to(&self, other: &PyAny) -> PyResult<f64> {
        if let Ok(point) = other.extract::<f64>() {
            if self.overlaps(point) {
                Ok(0.0)
            } else if point < self.begin {
                Ok(self.begin - point)
            } else {
                Ok(point - self.end)
            }
        } else if let Ok(other_iv) = other.extract::<Interval>() {
            if self.overlaps_interval(&other_iv) {
                Ok(0.0)
            } else if self.begin >= other_iv.end {
                Ok(self.begin - other_iv.end)
            } else {
                Ok(other_iv.begin - self.end)
            }
        } else {
            Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                "distance_to requires a number or Interval",
            ))
        }
    }

    /// Returns the size of the overlap between this interval and the given point or range.
    ///
    /// For a range [begin, end), returns the length of the overlapping region.
    /// For a point, returns 1 if the point is contained, 0 otherwise.
    #[pyo3(signature = (begin, end=None))]
    pub fn overlap_size(&self, begin: f64, end: Option<f64>) -> f64 {
        if let Some(end_val) = end {
            let overlap_begin = self.begin.max(begin);
            let overlap_end = self.end.min(end_val);
            (overlap_end - overlap_begin).max(0.0)
        } else if self.overlaps(begin) {
            1.0
        } else {
            0.0
        }
    }

    /// Checks if this interval has the same begin and end as another, ignoring data.
    pub fn range_matches(&self, other: &Interval) -> bool {
        self.begin == other.begin && self.end == other.end
    }

    /// Returns a shallow copy of this interval.
    pub fn copy(&self) -> Interval {
        self.clone()
    }

    /// String representation of the interval.
    fn __repr__(&self, py: Python) -> PyResult<String> {
        let data_str = self.data.as_ref(py).str()?.to_str()?;
        let start_bracket = if self.start_inclusive { "[" } else { "(" };
        let end_bracket = if self.end_inclusive { "]" } else { ")" };
        Ok(format!(
            "Interval{}{}, {}{} data={}",
            start_bracket, self.begin, self.end, end_bracket, data_str
        ))
    }

    /// Returns the length of the interval tuple (always 3: begin, end, data).
    fn __len__(&self) -> usize {
        3
    }

    /// Access interval components by index: 0=begin, 1=end, 2=data.
    fn __getitem__(&self, idx: isize) -> PyResult<PyObject> {
        Python::with_gil(|py| match idx {
            0 => Ok(self.begin.into_py(py)),
            1 => Ok(self.end.into_py(py)),
            2 => Ok(self.data.clone()),
            _ => Err(PyIndexError::new_err(
                "Interval index out of range (valid: 0, 1, 2)",
            )),
        })
    }

    /// Allow unpacking Interval objects as (begin, end, data) with custom iteration.
    fn __iter__(slf: PyRef<Self>) -> PyResult<Py<IntervalIter>> {
        let py = slf.py();
        let data = vec![slf.begin.into_py(py), slf.end.into_py(py), slf.data.clone()];
        Py::new(py, IntervalIter { data, index: 0 })
    }

    /// Equality comparison for intervals.
    fn __eq__(&self, other: &PyAny) -> PyResult<bool> {
        if let Ok(other_interval) = other.extract::<Interval>() {
            let data_equal = Python::with_gil(|py| {
                match (
                    self.data.as_ref(py).is(other_interval.data.as_ref(py)),
                    self.data.as_ref(py).eq(other_interval.data.as_ref(py)),
                ) {
                    (true, _) => true,         // Same object
                    (false, Ok(true)) => true, // Equal content
                    _ => false,                // Different or comparison failed
                }
            });

            Ok(self.begin == other_interval.begin
                && self.end == other_interval.end
                && self.start_inclusive == other_interval.start_inclusive
                && self.end_inclusive == other_interval.end_inclusive
                && data_equal)
        } else {
            Ok(false)
        }
    }

    /// Hash function for intervals.
    fn __hash__(&self) -> PyResult<isize> {
        // Simple hash combining begin, end, and data hash
        let begin_hash = self.begin.to_bits() as isize;
        let end_hash = self.end.to_bits() as isize;
        let data_hash = Python::with_gil(|py| self.data.as_ref(py).hash().unwrap_or(0));

        // Combine hashes using a simple method
        Ok(begin_hash
            .wrapping_mul(31)
            .wrapping_add(end_hash.wrapping_mul(31))
            .wrapping_add(data_hash))
    }

    /// Rich comparison method for intervals.
    ///
    /// Intervals are ordered first by begin, then by end.
    fn __richcmp__(&self, other: &PyAny, op: pyo3::basic::CompareOp) -> PyResult<PyObject> {
        use pyo3::basic::CompareOp;

        if let Ok(other_interval) = other.extract::<Interval>() {
            let result = match op {
                CompareOp::Lt => {
                    self.begin < other_interval.begin
                        || (self.begin == other_interval.begin && self.end < other_interval.end)
                }
                CompareOp::Le => {
                    self.begin < other_interval.begin
                        || (self.begin == other_interval.begin && self.end <= other_interval.end)
                }
                CompareOp::Eq => self.__eq__(other)?,
                CompareOp::Ne => !self.__eq__(other)?,
                CompareOp::Gt => {
                    self.begin > other_interval.begin
                        || (self.begin == other_interval.begin && self.end > other_interval.end)
                }
                CompareOp::Ge => {
                    self.begin > other_interval.begin
                        || (self.begin == other_interval.begin && self.end >= other_interval.end)
                }
            };

            Python::with_gil(|py| Ok(result.into_py(py)))
        } else {
            // Can't compare with non-Interval types for ordering
            match op {
                CompareOp::Eq => Ok(false.into_py(other.py())),
                CompareOp::Ne => Ok(true.into_py(other.py())),
                _ => Err(PyErr::new::<pyo3::exceptions::PyTypeError, _>(
                    "Intervals can only be compared with other Intervals",
                )),
            }
        }
    }

    /// Checks if this interval is enveloped by a range.
    ///
    /// Returns `true` if this interval is completely contained within [start, end).
    /// The enveloping range is assumed to be [start, end) (start inclusive, end exclusive).
    pub fn enveloped_by(&self, start: f64, end: f64) -> bool {
        // For interval [a,b] to be enveloped by range [start,end):
        // - Interval start must be >= start: a >= start (respecting interval's start inclusivity)
        // - Interval end must be < end: b < end (respecting interval's end inclusivity)

        let start_contained = if self.start_inclusive {
            // If interval start is inclusive, it's contained if start <= self.begin
            start <= self.begin
        } else {
            // If interval start is exclusive, it's contained if start < self.begin
            start < self.begin
        };

        let end_contained = if self.end_inclusive {
            // If interval end is inclusive, it must be < end for containment in [start,end)
            self.end < end
        } else {
            // If interval end is exclusive, it must be <= end for containment in [start,end)
            self.end <= end
        };

        start_contained && end_contained
    }
}

/// Iterator for the Interval class.
#[pyclass]
pub struct IntervalIter {
    pub(crate) data: Vec<PyObject>,
    pub(crate) index: usize,
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
