from manzanita import Interval, IntervalTree


class PyInterval:
    def __init__(self, begin, end, data):
        self.interval = Interval(begin, end, data)

    def __repr__(self):
        return self.interval.__repr__()

    def __len__(self):
        return len(self.interval)

    def __getitem__(self, idx):
        return self.interval.__getitem__(idx)

    def __iter__(self):
        return iter(self.interval)

    @property
    def begin(self):
        return self.interval.begin

    @begin.setter
    def begin(self, value):
        self.interval.begin = value

    @property
    def end(self):
        return self.interval.end

    @end.setter
    def end(self, value):
        self.interval.end = value

    @property
    def data(self):
        return self.interval.data

    # Additional methods from the Rust implementation
    def overlaps(self, point):
        return self.interval.overlaps(point)

    def overlaps_range(self, start, end):
        return self.interval.overlaps_range(start, end)


class PyIntervalTree:
    def __init__(self):
        self.tree = IntervalTree()

    def add(self, interval):
        if isinstance(interval, PyInterval):
            self.tree.add(interval.interval)
        else:
            raise TypeError("Expected PyInterval instance")

    def at(self, point):
        return [PyInterval(i.begin, i.end, i.data) for i in self.tree.at(point)]

    def overlap(self, start, end):
        return [PyInterval(i.begin, i.end, i.data) for i in self.tree.overlap(start, end)]

    def __getitem__(self, idx):
        intervals = self.tree.__getitem__(idx)
        return [PyInterval(i.begin, i.end, i.data) for i in intervals]

    def __len__(self):
        return len(self.tree)

    def __iter__(self):
        return iter(self.tree)

    def __repr__(self):
        return repr(self.tree)

    # Additional helper methods
    def collect_intervals(self):
        """Collects all intervals in the tree."""
        intervals = []
        for interval in self:
            intervals.append(PyInterval(interval.begin, interval.end, interval.data))
        return intervals
