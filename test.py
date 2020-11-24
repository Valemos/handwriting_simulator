import os
import unittest
from pathlib import Path

from handwriting.path_group import PathGroup
from handwriting.handwritten_path import HandwrittenPath, Curve, Point


# class TestRemoveIndex(unittest.TestCase):
#
#     def test_remove_index(self):
#         test_path = Path("my_letters/а.hndw")
#         temp = Path("temp.hndw")
#
#         with test_path.open("rb") as fin, temp.open("wb+") as fout:
#             fout.write(fin.read())
#
#         group = PathGroup.from_file(temp)
#
#         group.remove_by_index(3)
#
#         other = PathGroup.from_file(temp)
#         self.assertEqual(group, other)
#
#         os.remove(temp)


class TestConvertCurve(unittest.TestCase):

    def test_path_to_bytes(self):
        a = HandwrittenPath('hello',
                            [
                                Curve([Point(1, 100), Point(50, 50), Point(20, 111), Point(50, 66)]),
                                Curve([Point(50, 56), Point(10, 70)])
                            ])
        bt = a.get_bytes()

        b = HandwrittenPath.from_bytes(bt)
        self.assertEqual(a, b)

class TestShiftPosition(unittest.TestCase):

    abs_points = [Point(*elem) for elem in [(15, 15), (20, 15), (30, 40), (80, 60)]]

    def test_curve_appends(self):

        cr = Curve.from_absolute(list(self.abs_points))

        cr.append_absolute(Point(100, 118))
        self.assertEqual(Point(100, 118), cr._last_absolute_point)

        cr.append_shift(Point(10, 11))
        self.assertEqual(Point(110, 129), cr.calc_last_point())


    def test_curve_iteration(self):
        cr = Curve.from_absolute(list(self.abs_points))

        # must exit
        for points in Curve():
            pass

        index = 0
        for abs_point in cr:
            self.assertEqual(abs_point, self.abs_points[index])
            index += 1


if __name__ == '__main__':
    unittest.main()
