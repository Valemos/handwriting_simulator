import pickle

from handwriting.point import Point

class Curve:
    """
    this class combines set of abs_points for handwritten path
    each point stored as shift relative to previous point
    """
    def __init__(self, points=None):
        if points is None:
            self.shifts = []
        else:
            self.shifts = points

    def __eq__(self, other):
        return all(map(lambda x, y: x == y, self.shifts, other.shifts))

    def get_bytes(self):
        try:
            return pickle.dumps(self.shifts)
        except pickle.PicklingError:
            print("error saving curve to bytes")
            return bytes()

    @staticmethod
    def from_bytes(curve_bytes):
        try:
            return Curve(pickle.loads(curve_bytes))
        except pickle.UnpicklingError:
            print("error loading curve from bytes")
            return None

    def append_shift(self, x, y):
        self.shifts.append(Point(x, y))

    @staticmethod
    def from_absolute(abs_points: list):
        if len(abs_points) == 0:
            return Curve()

        new_curve = Curve([abs_points[0]])
        for i in range(1, len(abs_points)):
            new_curve.append_shift(*abs_points[i].get_shift(abs_points[i - 1]))

    def get_absolute(self, shift_point: Point):
        new_points = [shift_point]
        for shift_amount in self.shifts[1:]:
            new_points.append(new_points[-1].shift(shift_amount))
        return new_points
