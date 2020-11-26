import io
import os
import unittest
from unittest.mock import patch
from pathlib import Path
import copy

from handwriting.path_group import PathGroup
from handwriting.handwritten_path import HandwrittenPath, Curve, Point
from handwriting.signature_dictionary import SignatureDictionary

abs_points = [Point(*elem) for elem in [(15, 15), (20, 15), (30, 40), (80, 60)]]
test_path = HandwrittenPath('hello',
                            [
                                Curve([Point(1, 10), Point(1, 10), Point(1, 10), Point(1, 10)]),
                                Curve([Point(10, 100), Point(10, 100)])
                            ])

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
        a = copy.deepcopy(test_path)
        bt = a.get_bytes()

        b = HandwrittenPath.read_next(io.BytesIO(bt))
        self.assertEqual(a, b)


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
            self.assertEqual(abs_point, abs_points[index])
            index += 1

class TestDictionary(unittest.TestCase):

    @patch("handwriting.signature_dictionary.SignatureDictionaryIterator.current")
    def test_dict_iterator(self, *mocks):
        obj = SignatureDictionary.from_file(Path('paths_format_transition/anton_test.dict'))
        it = obj.get_iterator()

        for i in range(100):
            print(it.cur_group, it.cur_variant)
            it.prev()

if __name__ == '__main__':
    unittest.main()
