from handwriting.misc.i_lines_iterator import ILinesIterator
from handwriting.misc.updateable_iterator import UpdatableIterator
from handwriting.path.curve.lines_iterator import CurveLinesIterator


class PathLinesIterator(ILinesIterator):
    """
    this class returns pairs of points to properly draw lines on canvas
    """

    def __init__(self, path, shift=None):
        self.path = path

        self.curves_iterator = UpdatableIterator(self.path.components)
        self.points: tuple = None, None

        self.lines_iterator: CurveLinesIterator = None
        if len(self.curves_iterator) > 0:
            self._iterate_next_curve(shift)

    def __next__(self):
        if self.lines_iterator is None:
            self._iterate_next_curve()

        self.points = next(self.lines_iterator)

        if self.lines_iterator.is_finished():
            self.lines_iterator.set_finished(False)  # enables iterating when new points are added
            self._iterate_next_curve(self.points[1])
            self.__next__()

        return self.points

    def _iterate_next_curve(self, shift=None):
        self.lines_iterator = next(self.curves_iterator).get_lines(shift)

    def _new_curve(self, point):
        """
        point must be absolute value as needed to be returned by this iterator later
        """
        self.path.new_curve(point, self.points[-1] if self.points is not None else None)

    def append_absolute(self, point):
        self.path.append_absolute(point)
