from manzanita import Interval, IntervalTree

# Create a new IntervalTree
tree = IntervalTree()

# Create intervals without data (will default to None)
Interval(1.0, 5.5)

# Add intervals to the tree
tree.add(Interval(1.0, 5.5, "data1"))
tree.add(Interval(1.0, 5.5, "data1"))
tree.add(Interval(3.3, 7.7, "data2"))
tree.add(Interval(6.6, 9.9, "data3"))

# Also works without data parameter
tree.add(Interval(0.5, 2.0))  # data will be None
tree.add(Interval(8.0, 10.0))  # data will be None

# Query intervals overlapping a point
print("Intervals at point 4.4:")
for interval in tree[4.4]:
    print(interval)

# Query intervals overlapping a range
print("\nIntervals overlapping range [2.2,6.6):")
for interval in tree[2.2:6.6]:
    print(interval)

# Use methods directly
print("\nIntervals at point 7.7:")
for interval in tree.at(7.7):
    print(interval)

print("\nIntervals overlapping range [5.5,8.8):")
for interval in tree.overlap(5.5, 8.8):
    print(interval)

# Iterate over the tree
print("\nAll intervals in the tree:")
for interval in tree:
    print(interval)

# Get the number of intervals
print(f"\nNumber of intervals in the tree: {len(tree)}")

# Unpack an interval
iv = Interval(10.0, 15.5, "data4")
begin, end, data = iv
print(f"\nUnpacked interval: begin={begin}, end={end}, data={data}")

# Examples without data
iv_no_data = Interval(20.0, 25.0)  # data defaults to None
begin, end, data = iv_no_data
print(f"Interval without data: begin={begin}, end={end}, data={data}")
