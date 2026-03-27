# Manzanita

A high-performance interval tree library implemented in Rust with Python bindings via [PyO3](https://pyo3.rs/). Drop-in alternative to [intervaltree](https://github.com/chaimleib/intervaltree) with significantly better performance.

## Installation

```bash
pip install manzanita
```

### From source

```bash
pip install maturin
git clone https://github.com/pgarrett-scripps/manzanita.git
cd manzanita
maturin develop --release
```

## Quick Start

```python
from manzanita import Interval, IntervalTree

# Create a tree and add intervals
tree = IntervalTree()
tree.add(Interval(1.0, 5.0, "alpha"))
tree.add(Interval(3.0, 8.0, "beta"))
tree.add(Interval(10.0, 15.0, "gamma"))

# Or use shorthand
tree.addi(20.0, 25.0, "delta")

# Query by point
tree.at(4.0)          # intervals containing point 4.0
tree[4.0]             # same thing, using indexing syntax

# Query by range
tree.overlap(2.0, 6.0)   # intervals overlapping [2, 6)
tree[2.0:6.0]             # same thing, using slice syntax

# Find intervals completely contained in a range
tree.envelop(0.0, 9.0)

# Check for overlaps
tree.overlaps(4.0)          # True - any interval contains 4.0?
tree.overlaps(2.0, 6.0)     # True - any interval overlaps [2, 6)?

# Create from tuples
tree = IntervalTree.from_tuples([
    (1, 3),
    (2, 4, "with data"),
    (5, 7),
])
```

## Interval Operations

```python
iv = Interval(1.0, 5.0, "data")
iv.begin       # 1.0
iv.end         # 5.0
iv.data        # "data"

# Tuple unpacking
begin, end, data = iv

# Overlap checks
iv.overlaps(3.0)                  # point overlap
iv.overlaps_range(2.0, 4.0)      # range overlap
iv.overlaps_interval(other_iv)    # interval overlap
```

## Deletion

```python
tree.remove(interval)         # raises ValueError if not found
tree.discard(interval)        # silent if not found
tree.removei(1.0, 5.0, "data")
tree.discardi(1.0, 5.0, "data")

# Remove by overlap
tree.remove_overlap(4.0)        # remove all containing point
tree.remove_overlap(2.0, 6.0)   # remove all overlapping range
tree.remove_envelop(2.0, 6.0)   # remove all enveloped by range

# Indexing syntax
del tree[4.0]       # remove all containing point
del tree[2.0:6.0]   # remove all overlapping range

tree.clear()   # remove everything
iv = tree.pop()  # remove and return an arbitrary interval
```

## Set Operations

```python
tree1 | tree2    # union
tree1 & tree2    # intersection
tree1 - tree2    # difference
tree1 ^ tree2    # symmetric difference

tree1 |= tree2   # in-place union
tree1 &= tree2   # in-place intersection
tree1 -= tree2   # in-place difference
tree1 ^= tree2   # in-place symmetric difference

tree1 <= tree2   # subset
tree1 >= tree2   # superset
tree1 == tree2   # equality
```

## Restructuring

```python
# Split all intervals at their mutual boundary points
tree.split_overlaps()

# Merge overlapping intervals
tree.merge_overlaps()
tree.merge_overlaps(strict=False)  # also merge touching intervals

# Merge intervals with identical ranges
tree.merge_equals()

# Merge adjacent/nearby intervals
tree.merge_neighbors()
tree.merge_neighbors(max_dist=1.0)

# Chop out a range (split intervals at boundaries, remove the middle)
tree.chop(3.0, 7.0)

# Slice all intervals at a point
tree.slice(5.0)
```

All restructuring methods accept an optional `datafunc` parameter to control how data is combined or transformed.

## Boundary Inclusivity

By default, intervals are half-open `[begin, end)` (inclusive start, exclusive end). This can be configured per-interval or as a tree default:

```python
# Per-interval
iv = Interval(1.0, 5.0, "data", start_inclusive=True, end_inclusive=True)  # [1, 5]
iv = Interval(1.0, 5.0, "data", start_inclusive=False, end_inclusive=False)  # (1, 5)

# Tree default (applies to addi, from_tuples)
tree = IntervalTree(start_inclusive=True, end_inclusive=True)
tree.addi(1.0, 5.0, "data")  # creates [1, 5]
```

## Tree Information

```python
len(tree)        # number of intervals
bool(tree)       # True if non-empty
tree.is_empty()  # True if empty
tree.begin()     # minimum begin value
tree.end()       # maximum end value
tree.items()     # list of all intervals

# Membership
interval in tree
tree.containsi(1.0, 5.0, "data")

# Iteration
for interval in tree:
    print(interval.begin, interval.end, interval.data)
```

## Performance

Manzanita is implemented in Rust and compiled as a native Python extension. Key operations have the following time complexity:

| Operation | Time Complexity |
|-----------|----------------|
| `add` / `addi` | O(log n) |
| `at` / `overlap` / `envelop` | O(log n + k) |
| `remove` / `discard` | O(n) |
| `len` | O(n) |
| `begin` / `end` | O(n) |

Where *n* is the number of intervals and *k* is the number of results.

## License

MIT
