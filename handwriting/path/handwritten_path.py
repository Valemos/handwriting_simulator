from typing import Iterator

from handwriting.path.curve.curve import Curve
from handwriting.path.curve.i_line_iterable import ILinesIterable
from handwriting.path.curve.point import Point
from handwriting.path.i_curve_collection import ICurveCollection
from handwriting.path.path_lines_iterator import PathLinesIterator
from handwriting.misc.stream_savable import IStreamSavable
from handwriting.path.i_collection import ICollection


class HandwrittenPath(ICollection, ICurveCollection, IStreamSavable):
    """
    Contains name for path and list of components (canvas_objects of type Curve),
    which represent separate sets of shifts
    """

    def __init__(self, name='', curves: list = None):
        super().__init__(curves)
        self.name = name

    def __iter__(self):
        return PathLinesIterator(self)

    def get_lines(self, shift: Point = None) -> PathLinesIterator:
        return PathLinesIterator(self, shift)

    def get_curves(self):
        return self.components

    def set_position(self, point: Point):
        if len(self.components) > 0:
            self.components[0].set_position(point)
            self.get_last_point()

    def get_position(self):
        if len(self.components) > 0:
            return self.components[0].prev_point
        else:
            return Point(0, 0)

    def new_curve(self, start: Point, previous: Point = None):
        previous = previous if previous is not None else Point(0, 0)
        curve_shift = start.get_shift(previous)

        curve = Curve(start=curve_shift)
        curve.last_absolute_point = start  # must be assigned to continue adding points to curve

        self.components.append(curve)

    def append_shift(self, point: Point):
        if len(self.components) > 0:
            self.components[-1].append_shift(point)
        else:
            self.new_curve(point)

    def append_absolute(self, point: Point):
        if len(self.components) > 0:
            self.components[-1].append_absolute(point)
        else:
            self.new_curve(point)

    def empty(self):
        return len(self.components) > 0

    def append_path(self, other_path):
        self.components.extend(other_path.components)

    def get_last_point(self):
        last_point = Point(0, 0)
        for curve in self.components:
            last_point = curve.get_last_point(last_point)
        return last_point

    def append(self, path: ILinesIterable):
        self.components.append(path)

    @staticmethod
    def empty_instance():
        return HandwrittenPath("")
