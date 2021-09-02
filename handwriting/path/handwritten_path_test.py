import copy
import io
import unittest

from handwriting.path.curve.curve import Curve
from handwriting.path.handwritten_path import HandwrittenPath
from handwriting.path.curve.point import Point


class TestHandwrittenPath(unittest.TestCase):

    @staticmethod
    def init_path():
        return HandwrittenPath(curves=[
            Curve([Point(1, 1), Point(1, 1), Point(1, 1)]),
            Curve(start_shift=Point(10, 10)),
            Curve([Point(1, 1)])])

    @staticmethod
    def init_absolute_points():
        return [Point(*elem) for elem in [(15, 15), (20, 15), (30, 40), (80, 60)]]

    def setUp(self):
        self.path = self.init_path()
        self.curve = self.path[0]
        self.empty_path = HandwrittenPath()
        self.abs_points = self.init_absolute_points()

    def test_create_empty_path(self):
        self.assertEqual(self.empty_path.get_last_point(), Point(0, 0))
        self.assertTrue(self.empty_path.empty())

    def test_set_path_position(self):
        self.path.set_position(Point(10, 10))
        self.assertEqual(self.path.get_last_point(), Point(24, 24))

    def test_append_shift_to_path(self):
        self.empty_path.append_shift(Point(1, 1))
        self.assertEqual(self.empty_path.get_last_point(), Point(1, 1))
        self.empty_path.append_shift(Point(10, 10))
        self.assertEqual(self.empty_path.get_last_point(), Point(11, 11))

    def test_curve_last_point(self):
        self.assertEqual(self.curve.get_last_point(), Point(3, 3))
        self.assertEqual(self.curve.get_last_point(Point(10, 10)), Point(13, 13))

    def test_path_to_bytes(self):
        a = copy.deepcopy(self.path)
        bt = a.get_bytes()

        b = HandwrittenPath.read_next(io.BytesIO(bt))
        self.assertEqual(a, b)

    def test_path_with_shift_to_bytes(self):
        self.path.set_position(Point(10, 10))
        a = copy.deepcopy(self.path)
        bt = a.get_bytes()

        b = HandwrittenPath.read_next(io.BytesIO(bt))
        self.assertEqual(a, b)

    def test_curve_from_absolute_points(self):
        curve = Curve.from_absolute(list(self.abs_points)).get_iterator()
        list_iter = iter(self.abs_points)
        while True:
            try:
                self.assertEqual(next(curve), next(list_iter))
            except StopIteration:
                break
