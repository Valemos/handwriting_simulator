from collections import Iterator

from handwriting.misc.updateable_iterator import UpdatableIterator
from handwriting.path.curve.point import Point


class CurvePointsIterator(Iterator):
    """
    This class iterates through shifts in Curve
    and returns absolute values of points relative to initial shift
    """

    def __init__(self, curve, shift=None):
        self.parent = curve
        self.cur_point = curve.get_start_shift(shift)
        self.shifts_iterator = UpdatableIterator(curve.components)

    def __len__(self):
        return len(self.parent)

    def __next__(self) -> Point:
        """
        Each iteration shifts previous point by next value from Curve shifts
        """

        self.cur_point = self.cur_point.shift(next(self.shifts_iterator))
        return self.cur_point
