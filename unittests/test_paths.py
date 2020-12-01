import copy
import io
import unittest

import sys
sys.path.append(r"D:\coding\Python_codes\Handwriting_extractor_project")

from handwriting.path_management.curve import Curve
from handwriting.path_management.handwritten_path import HandwrittenPath
from handwriting.path_management.point import Point

abs_points = [Point(*elem) for elem in [(15, 15), (20, 15), (30, 40), (80, 60)]]
test_path = HandwrittenPath('hello',
                            [
                                Curve([Point(1, 10), Point(1, 10), Point(1, 10), Point(1, 10)]),
                                Curve([Point(10, 100), Point(10, 100)])
                            ])

class TestPath(unittest.TestCase):

    def test_path_iteration(self):
        path = copy.deepcopy(test_path)
        it = iter(path)
        val = next(it)
        self.assertEqual(val[0], Point(1, 10))
        self.assertEqual(val[1], Point(2, 20))
        next(it)
        next(it)

        last_point = path.components[0].calc_last_point()
        prev_point = last_point.shift(path.components[1].components[0])
        cur_point = prev_point.shift(path.components[1].components[1])

        self.assertEqual(next(it), (prev_point, cur_point))


class TestShiftPosition(unittest.TestCase):

    def test_curve_appends(self):

        cr = Curve.from_absolute(list(abs_points))

        cr.append_absolute(Point(100, 118))
        self.assertEqual(Point(100, 118), cr.last_absolute_point)

        cr.append_shift(Point(10, 11))
        self.assertEqual(Point(110, 129), cr.calc_last_point())


    def test_curve_iteration(self):
        cr = Curve.from_absolute(list(abs_points))

        # must exit
        for points in Curve():
            pass

        index = 0
        for abs_point in cr:
            print(abs_point, abs_points[index])
            index += 1


class TestConvertCurve(unittest.TestCase):

    def test_path_to_bytes(self):
        a = copy.deepcopy(test_path)
        bt = a.get_bytes()

        b = HandwrittenPath.read_next(io.BytesIO(bt))
        self.assertEqual(a, b)

