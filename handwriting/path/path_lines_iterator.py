from collections import Iterator

from handwriting.path.curve.lines_iterator import LinesIterator
from handwriting.misc.updateable_iterator import UpdatableIterator


class PathLinesIterator(Iterator):
    """
    this class returns pairs of points to properly draw lines on canvas
    """

    def __init__(self, obj, shift=None):
        self.path = obj

        self.curves_iterator = UpdatableIterator(self.path.components)
        self.points: tuple = None, None

        self.lines_iterator: LinesIterator = None
        if len(self.curves_iterator) > 0:
            self.iterate_next_curve(shift)

    def __next__(self):
        if self.lines_iterator is None:
            self.iterate_next_curve()

        self.points = self.lines_iterator.next()

        if self.lines_iterator.is_finished():
            self.lines_iterator.finished = False  # enables iterating when new points are added
            self.iterate_next_curve(self.points[1])
            self.__next__()

        return self.points

    def iterate_next_curve(self, shift=None):
        self.lines_iterator = next(self.curves_iterator).get_lines(shift)

    def new_curve(self, point):
        """
        point must be absolute value as needed to be returned by this iterator later
        """
        self.path.new_curve(point, self.points[-1] if self.points is not None else None)

    def append_absolute(self, point):
        self.path.append_absolute(point)
