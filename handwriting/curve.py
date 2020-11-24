import pickle

from handwriting.point import Point

class CurveIterator:
    """
    This class iterates through shifts in Curve
    and returns absolute values of points
    """
    def __init__(self, obj):
        self.obj = obj
        self.first_point = obj.shifts[0] if len(obj.shifts) > 0 else None
        self._cur_point = self.first_point
        self._shifts_iter = iter([Point(0, 0)] + obj.shifts[1:])

    def __next__(self):
        if self.first_point is None:
            raise StopIteration

        # shifts iterator will raise StopIteration
        # and each iterator will correctly stop
        next_shift = next(self._shifts_iter)
        self._cur_point = self._cur_point.shift(next_shift)
        return self._cur_point


class Curve:
    """
    Contains set of shifts for handwritten path
    with each point stored as shift relative to previous point
    """
    def __init__(self, shifts=None):

        self.shifts = [] if shifts is None else shifts

        # absolute point used to calculate next shift point for append function
        self._last_absolute_point = self.calc_last_point()

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.shifts, other.shifts))

    def __len__(self):
        return len(self.shifts)

    def __iter__(self):
        return CurveIterator(self)

    def set_position(self, point: Point):
        """
        Zero position plays a role of shift relative to (0, 0) position
        :param point: point to set position to
        """
        self.shifts[0] = point

    @staticmethod
    def convert_abs_to_shifts(abs_points: list):
        """
        Takes as input list of Point objects
        :param abs_points: list of absolute points
        :return:
        """
        new_points = [abs_points[0]]
        prev_point = abs_points[0]
        for point in abs_points[1:]:
            new_points.append(point.prev_point.get_shift(prev_point))
            prev_point = point
        return new_points

    def get_bytes(self):
        """dump self.shifts list to bytes"""
        try:
            return pickle.dumps(self.shifts)
        except pickle.PicklingError:
            print("error saving curve to bytes")
            return bytes()

    @staticmethod
    def from_bytes(curve_bytes):
        """loads shifts list from bytes and initializes Curve object"""
        try:
            return Curve(pickle.loads(curve_bytes))
        except pickle.UnpicklingError:
            print("error loading curve from bytes")
            return None

    def append_shift(self, point: Point):
        self.shifts.append(point)
        self._last_absolute_point.shift(point)

    def append_absolute(self, point: Point):
        """
        Method appends shift relative to previous absolute point recorded in self._last_absolute_point
        value of self._last_absolute_point is changed for the next append operation
        """

        self.shifts.append(point.get_shift(self._last_absolute_point))
        self._last_absolute_point = point

    @staticmethod
    def from_absolute(abs_points: list):
        """Returns instance of Curve for absolute values of points"""
        if len(abs_points) == 0:
            return Curve()

        new_curve = Curve()
        for p in abs_points:
            new_curve.append_absolute(p)
        return new_curve

    def get_absolute_iterator(self, anchor: Point):
        """
        This function creates set of absolute points shifted relative to first point,
        first point is equal to the anchor point

        :param anchor:
        :return: iterator in list of absolute points relative to anchor point
        """
        new_points = [anchor]
        for shift_amount in self.shifts[1:]:
            new_points.append(new_points[-1].shift(shift_amount))
        return new_points

    def calc_last_point(self):
        """
        Method calculates absolute position of last point using self.shifts list.
        First point in self.shifts is considered as a starting point.
        Each next point is a relative shift from previous point.

        If shifts list is empty, resulting point is considered to be (0, 0)

        :returns absolute value for last point in shifts list
        """
        if len(self.shifts) == 0:
            return Point(0, 0)

        point = self.shifts[0]
        for i in range(1, len(self.shifts)):
            point = point.shift(self.shifts[i])
        return point
