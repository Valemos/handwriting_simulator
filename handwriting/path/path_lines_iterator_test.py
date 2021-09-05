from unittest import TestCase

from handwriting.path.curve.point import Point
from handwriting.path.handwritten_path import HandwrittenPath


class TestPathLinesIterator(TestCase):

    def setUp(self) -> None:
        self.path = HandwrittenPath()
        self.path.new_curve(Point(0, 0))
        self.path.append_shift(Point(1, 2))
        self.path.append_shift(Point(1, 2))
        self.path.new_curve(Point(10, 20))
        self.path.new_curve(Point(10, 20))
        self.path.append_shift(Point(1, 2))
        self.path.append_shift(Point(1, 2))
        self.path.get_last_point()

        self.path_iter = self.path.get_lines()

        self.expected_lines = [
            (Point(0, 0), Point(1, 2)),
            (Point(1, 2), Point(2, 4)),
            (Point(22, 44), Point(23, 46)),
            (Point(23, 46), Point(24, 48))
        ]

    @staticmethod
    def get_lines(path_iter):
        ls = []
        try:
            while True:
                ls.append(next(path_iter))
        except StopIteration:
            return ls

    def test_path_correct(self):
        self.assertListEqual(self.get_lines(self.path_iter), self.expected_lines)

    def test_create_new_curve_from_iterator(self):
        self.get_lines(self.path_iter)
        self.path_iter._new_curve(Point(50, 50))
        self.path_iter.append_absolute(Point(55, 55))
        self.path_iter.append_absolute(Point(60, 80))
        self.path_iter.append_absolute(Point(65, 85))

        lines = self.get_lines(self.path_iter)
        self.assertListEqual(lines, [
                                 (Point(50, 50), Point(55, 55)),
                                 (Point(55, 55), Point(60, 80)),
                                 (Point(60, 80), Point(65, 85))
                             ])

    def test_empty_path_filled(self):
        path = HandwrittenPath()

        itr = path.get_lines()

        itr._new_curve(Point(50, 50))
        itr.append_absolute(Point(55, 55))
        itr.append_absolute(Point(60, 80))
        itr.append_absolute(Point(65, 85))

        lines = self.get_lines(itr)
        self.assertListEqual(lines, [
            (Point(50, 50), Point(55, 55)),
            (Point(55, 55), Point(60, 80)),
            (Point(60, 80), Point(65, 85))
        ])
