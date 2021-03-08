from handwriting.path.curve.curve import Curve
from handwriting.path.curve.point import Point
from handwriting.path.path_lines_iterator import PathLinesIterator
from handwriting.path.stream_savable_collection import IStreamSavableCollection


class HandwrittenPath(IStreamSavableCollection):
    """
    Contains name for path and list of components (canvas_objects of type Curve),
    which represent separate sets of shifts
    """

    def __init__(self, name='', curves: list = None):
        super().__init__(curves)
        self.name = name

    def __iter__(self):
        return PathLinesIterator(self)

    def get_iterator(self, shift: Point = None) -> PathLinesIterator:
        return PathLinesIterator(self, shift)

    def set_position(self, point: Point):
        if len(self.components) > 1:
            self.components[0].start_shift = point
            self.calc_last_point()

    def get_position(self):
        if len(self.components) > 0:
            return self.components[0].previous_point
        else:
            return Point(0, 0)

    def new_curve(self, start_point: Point, previous_point: Point = None):
        previous_point = previous_point if previous_point is not None else Point(0, 0)
        relative_curve_shift = start_point.get_shift(previous_point)

        curve = Curve(start_shift=relative_curve_shift)
        curve.last_absolute_point = start_point

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
        return self.name == '' and len(self.components) > 0

    def append_path(self, other_path):
        self.components.extend(other_path.components)

    def calc_last_point(self):
        last_point = Point(0, 0)
        for curve in self.components:
            last_point = curve.get_last_point(last_point)
        return last_point
