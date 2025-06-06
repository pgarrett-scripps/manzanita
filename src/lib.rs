//! Manzanita: High-performance interval tree library
//!
//! This library provides fast interval tree data structures implemented in Rust
//! and exposed to Python via PyO3. It's optimized for applications requiring
//! frequent interval overlap queries.
//!
//! # Features
//! - Efficient O(log n + k) point and range queries
//! - Support for any associated data type
//! - Python-friendly API with indexing and iteration support
//! - Memory-efficient implementation using Arc for shared interval data
//! - Comprehensive interval operations: add, remove, query, envelop
//! - Python-compatible iteration and containment checking
//!
//! # Example
//! ```python
//! from manzanita import Interval, IntervalTree
//!
//! tree = IntervalTree()
//! tree.add(Interval(1.0, 5.0, "data1"))
//! tree.add(Interval(3.0, 7.0, "data2"))
//!
//! # Find intervals containing point 4.0
//! overlapping = tree.at(4.0)
//! 
//! # Create from tuples
//! tree2 = IntervalTree.from_tuples([(1, 3), (2, 4, "data")])
//! 
//! # Check containment
//! if Interval(1.0, 5.0, "data1") in tree:
//!     print("Found!")
//! ```

use pyo3::prelude::*;

// Public modules
pub mod interval;
pub mod tree;

// Internal modules
mod node;

// Re-export public types
pub use interval::{Interval, IntervalIter, BoundaryType};
pub use tree::{IntervalTree, IntervalTreeIter};

/// Python module for high-performance interval tree operations.
/// 
/// This module provides fast interval tree data structures implemented in Rust
/// and exposed to Python via PyO3. It's optimized for applications requiring
/// frequent interval overlap queries.
#[pymodule]
fn manzanita(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<Interval>()?;
    m.add_class::<IntervalIter>()?;
    m.add_class::<IntervalTree>()?;
    m.add_class::<IntervalTreeIter>()?;
    m.add_class::<BoundaryType>()?;
    Ok(())
}
