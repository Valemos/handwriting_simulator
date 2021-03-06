from handwriting.path.curve.curve_iterator import CurveIterator
from handwriting.path.curve.interface_iterable_curve import ICurveIterable
from handwriting.path.curve.lines_iterator import LinesIterator
from handwriting.path.curve.point import Point


class Curve(ICurveIterable):
    """
    Contains set of shifts for handwritten path
    with each point stored as last_point relative to previous point
    """

    def __init__(self, shifts: list = None, start_spacer: Point = None):
        self.start_spacer = start_spacer if start_spacer is not None else Point(0, 0)
        self.components = shifts if shifts is not None else []
        self.last_absolute_point = self.get_last_point()

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.components, other.components))

    def __len__(self):
        return len(self.components)

    def __getitem__(self, i):
        return self.components[i]

    def get_iterator(self, shift=None):
        return CurveIterator(self, shift)

    def get_lines(self, shift=None):
        return LinesIterator(self, shift)

    def append_shift(self, point: Point):
        self.components.append(point)
        self.last_absolute_point = self.last_absolute_point.shift(point)

    def append_absolute(self, point: Point):
        self.components.append(point.get_shift(self.last_absolute_point))
        self.last_absolute_point = point

    @staticmethod
    def from_absolute(abs_points: list):
        if len(abs_points) == 0:
            return Curve()

        new_curve = Curve()
        for p in abs_points:
            new_curve.append_absolute(p)
        return new_curve

    def get_last_point(self, shift=None):
        point = self.get_start_shift(shift)
        for i in range(len(self.components)):
            point = point.shift(self.components[i])

        self.last_absolute_point = point
        return point

    def get_start_shift(self, shift: Point = None):
        return self.start_spacer.shift(shift) if shift is not None else self.start_spacer

    @classmethod
    def create(cls, saved_content):
        return Curve(saved_content)

    def get_content_to_save(self):
        return self.components

    @staticmethod
    def empty_instance():
        return Curve()

    def empty(self):
        return len(self.components)
